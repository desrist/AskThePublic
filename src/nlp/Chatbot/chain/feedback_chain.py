# feedback_chain.py
import re
import os
import dotenv
import pandas as pd
from pymongo import MongoClient
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate, PipelinePromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA, ConversationalRetrievalChain, LLMChain
from langchain_openai import ChatOpenAI
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch # test
from langchain.memory import ConversationBufferMemory 
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain.schema import HumanMessage
from typing import List
import logging
import sys
import fitz
import json
import requests
import tempfile
import httpx
import asyncio

# utf-8
sys.stdout.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.INFO, encoding='utf-8')
logger = logging.getLogger(__name__)

# Load environment variables from the .env file
dotenv.load_dotenv()

# Initialize FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=86400
)

client = httpx.Client(timeout=60)

# Define parse_parameters function to create filter conditions
def parse_parameters(topic=None, userType=None):
    """
    Parse the input parameters and construct search conditions for MongoDB.
    Args:
    - topic (str): The topic to filter by. If 'None', no filtering by topic is applied.
    Returns:
    - dict: Constructed search conditions to be used in MongoDB Atlas VectorSearch.
    """
    conditions = {}

    if topic:
        conditions['topic'] = topic

    if userType and userType != 'ANY':
        conditions['userType'] = userType

    return conditions

# Get MongoDB Atlas credentials from environment variables
ATLAS_TOKEN = os.environ["ATLAS_TOKEN"]
ATLAS_USER = os.environ["ATLAS_USER"]
# Initialize MongoDB Connection
client = MongoClient(
    "mongodb+srv://{}:{}@cluster0.9tj38oe.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0".format(
            ATLAS_USER, ATLAS_TOKEN)
)
db_name = "metadata"
collection_name = "processed_feedback_data"
collection_search_name = "keywords_search_data"
collection_summary_name = "initiatives_summary_data"
collection = client[db_name][collection_name]

# Check for the OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Please set your API key in the OPENAI_API_KEY environment variable.")

# Set up embeddings, vectors, and memory for the retrieval chain
print("Setting up embeddings, vectors, and memory...")
embeddings = OpenAIEmbeddings(openai_api_key=api_key, 
                              model="text-embedding-3-small") # define embeddings to text-embedding-3-small

# Initialize vector search with pre-filter
vectors = MongoDBAtlasVectorSearch(
    collection=collection, 
    index_name='data_index',
    embedding=embeddings, 
    text_key='combined',
    embedding_key='embedding',
    relevance_score_fn="cosine",
)

prompt_template = """
    You are a helpful assistant responsible for providing detailed analysis and summaries of public opinion on EU laws and initiatives.

    ### Task:
    Your goal is to provide a structured and actionable analysis of public opinion. The analysis should be tailored to the questions asked, while maintaining clarity and relevance.
    
    ### Input:
    You are provided with the following:
    - **Question**: {question}. The question may come from policymakers, researchers, or citizens.
    - **Feedback Contexts**: {context}, which are retrieved from a database of citizen feedback.

    ### Context Structure:
    Each context provided to you includes the following information:
    - important **User Type** and **Organization**: The type of user or organization which are from context['UserType'] and context['Organization']
    - **Country**: The country of the feedback provider which can be ssen in context['Country']
    - **Real public opinion Content**: A real EU citizen feedback that can be seen in context['Content'] and context['Title']

    ### Requirements (Most of cases):
    1. **Analysis Structure**:
        - **Overview**:(about 100-150 words)
            - Provide a paragraph summary highlighting the key themes or sentiments across all feedbacks.
        - **Categorized Insights**:(about 300-400 words)
            - Group feedback by `User Type` and briefly summarize key points for each group.
            - Highlight unique perspectives, priorities, and concerns from each category.
        - **Actionable Insights**:(about 200-300 words)
            - Offer 2-3 specific, evidence-based recommendations or highlight conflicts that require resolution.
        - Special Cases: only meet below conditions:
            important: The following two situations are very special. Even if you are provided with context, please do not answer according to the usual structure.
            - If the context is not relevant to the question or if it is not possible to answer the question at all, please use it with caution and explain its limitations.
            - If the 'Question' does not align with analyzing information or public opinion on EU laws and initiatives: For example: 'What is the weather like today?'
                - Clearly explain the misalignment between the question and the program's capabilities.
                - For example:
                    "The provided question falls outside the scope of this program, which is designed to analyze and summarize public opinion on EU laws and initiatives. Although some context has been retrieved, its relevance to the question may be limited."
            
                            
    2. **Clarity**:
        - Important: Only use the information from the contexts provided to answer the question, and avoid speculation or using unprovided information.
        - Use concise paragraphs or bullet points for readability.
        - Avoid unnecessary jargon or technical terms unless contextually relevant.
        
    3. **Politeness**:
        - Maintain a friendly and professional tone.
            
    4. **Customizations Based on Input Question**:
        Important: - **Language**: Generate the response in the same language as the **Question**.
        - **Focus**: Tailor the depth of analysis based on the nature of the question (e.g., strategic, technical, or general). Prioritize the most relevant details.
        - **Format Preferences**: Adjust the response format based on user's question requirements.
            - Example: Provide a paragraph summary, bullet points, or categorized insights as requested.
        - Dynamically adapt the response format to match explicit or implicit user preferences.
        - Adapt the response lenghth based on the context given to you, for the most of cases, it is for 15 piece of contents.
"""    
QA_CHAIN_PROMPT = ChatPromptTemplate.from_template(prompt_template)

# memory = ConversationBufferMemory( 
#     memory_key='chat_history', 
#     return_messages=True,
#     output_key='answer'
#     ) 

def create_conversational_chain(llm, retriever):
    conversational_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        # memory=memory,
        combine_docs_chain_kwargs={"prompt": QA_CHAIN_PROMPT},
        return_source_documents=True,
        output_key='answer'
    )
    
    return conversational_chain

def create_retrieval_qa_chain(llm, retriever):
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
    )
    
    return qa_chain


''' Score Function Design, design a evaluation method to evaluate the quality and relevance of query, answer and source documents'''

@app.post("/query")
async def get_feedback(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        query = data.get("query")
        topic = data.get("topic") 
        usertype = data.get("userType")
        logger.info(f"usertype: {usertype}")
        logger.info(f"topic: {topic}")
        # logger.info(f"data: {data}")

        chain_type = data.get("chain_type", "retrievalqa")
        model_name = data.get("model_name", "gpt-4o-mini")
        search_type = data.get("search_type", "similarity")
        search_kwargs = data.get("search_kwargs", {'k': 15})
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required.")
        
        # Log the received query
        logger.info(f"Received query: {query}")
        
        # Generate pre-filter conditions using parse_parameters
        pre_filter_conditions = parse_parameters(topic=topic, userType=usertype)
        search_kwargs['pre_filter'] = pre_filter_conditions
        logger.info(f"Search kwargs: {search_kwargs}")
        
        # Dynamically create the LLM based on model_name
        llm = ChatOpenAI(temperature=0.5, model_name=model_name, openai_api_key=api_key, streaming=True)
        
        # creat retriever and use combined search_kwargs
        retriever = vectors.as_retriever(
            search_type=search_type,
            search_kwargs=search_kwargs
        )
        
        ''' Apply streaming output'''
        # Initialize the appropriate chain with streaming callbacks
        if chain_type == "conversational":
            chain = create_conversational_chain(llm, retriever)
            input_dict = {"question": query, "chat_history": []}
        elif chain_type == "retrievalqa":
            chain = create_retrieval_qa_chain(llm, retriever)
            input_dict = {"query": query}
        else:
            raise HTTPException(status_code=400, detail="Invalid chain type.")
        
        # Create an async iterator callback handler
        callback = AsyncIteratorCallbackHandler()
        # Start the chain execution in the background
        task = asyncio.create_task(chain.acall(inputs=input_dict, callbacks=[callback]))
        # Create an async generator to yield tokens as they are generated
        async def stream_response():
            try:
                # Stream tokens as they are generated
                async for token in callback.aiter():
                    if await request.is_disconnected():
                        logger.info("Client disconnected, stopping response.")
                        task.cancel()
                        break  # Stop streaming if client disconnects
                    yield token
                # After the chain is done, get the sources
                response = await task
                source_documents = response.get('source_documents', [])
                sources = [{"text": doc.page_content} for doc in source_documents]
                # Send a separator and then the sources
                # Send a special separator to indicate the end of the answer
                yield "\n<END_OF_ANSWER>\n"

                # Send the sources as JSON string
                sources_json = json.dumps(sources, ensure_ascii=False)
                logger.info(f"Sources JSON: {sources_json}")
                yield sources_json

            except asyncio.CancelledError:
                logger.info("Task cancelled due to client disconnect.")
                task.cancel()
            except Exception as e:
                logger.error(f"Error during streaming: {e}")
                
        return StreamingResponse(stream_response(), media_type="text/plain")

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# api for keywords search
collection_search = client[db_name][collection_search_name]

@app.get("/search_keywords", response_model=List[dict])
async def search_keywords(keyword: str = Query(..., min_length=1)):
    if not keyword or keyword.strip() == "":
        raise HTTPException(status_code=400, detail="Keyword parameter is required.")
    
    search_conditions = [
        {"shortTitle": {"$regex": keyword, "$options": "i"}},
        {"id": {"$regex": keyword, "$options": "i"}}
    ]
    results = list(collection_search.find(
        {
            "$or": search_conditions
        },
        {"_id": 0, "id": 1, "shortTitle": 1, "topic": 1, "totalFeedback": 1, "links": 1}
    ))
    
    if not results:
        raise HTTPException(status_code=404, detail="No matching documents found.")
    
    return results

# api for initiatives summary
initiatives_summary = client[db_name][collection_summary_name]

def download_pdf_to_tempfile(url):
    response = requests.get(url)
    response.raise_for_status()
    
    # create a temporary file to save the PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_file.write(response.content)
    temp_file.flush()
    temp_file.seek(0)
    
    logger.info(f"Downloaded PDF to temporary file: {temp_file.name}")
    return temp_file.name

def extract_text_from_pdf(file_path):
    document = fitz.open(file_path)
    text = ""
    
    # traverse each page and extract text
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
    
    logger.info(f"Extracted text from PDF: {file_path}")
    return text

@app.post("/generate_summary/{initiative_id}")
async def generate_summary(initiative_id):
    """
    Generate summary for the given initiative.
    """
    initiative_id = str(initiative_id)
    initiative = initiatives_summary.find_one({"initiative_id": initiative_id}, {"_id": 0, "attachments": 1})
    
    # If initiative does not exist, return 404
    if not initiative:
        raise HTTPException(status_code=404, detail="Initiative not found.")
    
    # Get the first attachment
    attachments = initiative.get("attachments", [])
    if not attachments or len(attachments) == 0:
        raise HTTPException(status_code=404, detail="No attachments found for this initiative.")
    
    attachment = attachments[0]
    attachment_url = attachment.get('downloadUrl', '')
    attachment_title = attachment.get('title', 'No Title')

    if not attachment_url:
        raise HTTPException(status_code=404, detail="Attachment download URL not found.")
    
    try:
        # Download the PDF and extract text
        pdf_file_path = download_pdf_to_tempfile(attachment_url)
        extracted_text = extract_text_from_pdf(pdf_file_path)
    except Exception as e:
        logger.error(f"Error during PDF download or text extraction: {e}")
        raise HTTPException(status_code=500, detail="Failed to download or extract text from PDF.")
    
    # Summarize the extracted text
    llm = ChatOpenAI(temperature=0.5, model_name="gpt-4o-mini", openai_api_key=api_key)
    summary_prompt = f"Please summarize the following text in less than 150 words: \n\n{extracted_text}\n\ntitle: {attachment_title}"
    
    # Generate summary with chain
    summary_chain = LLMChain(llm=llm, prompt=PromptTemplate(input_variables=["extracted_text", "attachment_title"], template=summary_prompt))
    summary_response = summary_chain.invoke({
        "extracted_text": extracted_text,
        "attachment_title": attachment_title
    })

    summary = summary_response.get('text', 'No summary generated.')
    
    return {
        "initiative_id": initiative_id,
        "attachment_title": attachment_title,
        "summary": summary
    }

# Run the FastAPI app using uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
    