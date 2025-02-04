import os
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import JSONResponse
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI 
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
import aiofiles
import dotenv
import tempfile


# load env 
dotenv.load_dotenv() 

# FastAPI app setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# openai setup
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Please set your API key in the OPENAI_API_KEY environment variable.")
embeddings = OpenAIEmbeddings(openai_api_key=api_key, model="text-embedding-3-small")
llm = ChatOpenAI(temperature=0.5, model_name='gpt-3.5-turbo', openai_api_key=api_key)

# define prompt
prompt_template =  """You are a helpful assistant providing detailed analysis and summaries of citizen feedback on EU laws and initiatives. 
You are provided with some part of documentation about citizen feedbacks.
Some of them may not be in English, so use your translation skills to understand them. 
Please answer in a friendly and natural manner, just like a normal conversation. 
If you don't know an answer, say you don't know.

Contexts:
{context}
Question: {question}
"""

QA_CHAIN_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=prompt_template,
    )

# clean data
def clean_text(text):
    return text.replace("\n", " ").replace("\r", " ").replace("\t", " ").lower()

# pdf to text
def load_and_split_pdf(file_path):
    pdf_reader = PyPDFLoader(file_path)
    docs = pdf_reader.load()
    # texts = [page.page_content for page in pages]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)
    # print(chunks)
    return chunks

# add chunks to vectorstore and qa chain
def create_qa_chain(chunks):
    cleaned_chunks = [clean_text(chunk.page_content) for chunk in chunks]
    print(cleaned_chunks)
    vectorstore = FAISS.from_texts(cleaned_chunks, embeddings)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    )
    
    return qa_chain, vectorstore

# upload pdf file
@app.post("/upload_pdf")
async def upload_pdf(files: List[UploadFile] = File(...)):
    try:
        all_chunks = []
        for file in files:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save the uploaded file to a temporary directory
                temp_file_path = os.path.join(temp_dir, file.filename)
                with open(temp_file_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                    text_chunks = load_and_split_pdf(temp_file_path)
                    all_chunks.extend(text_chunks)
        
        qa_chain, vectorstore = create_qa_chain(all_chunks)
        
        app.state.vectorstore = vectorstore
        app.state.qa_chain = qa_chain
        
        return {"message": "PDF files uploaded and processed successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# query
@app.post("/query")
async def get_feedback(request: Request):
    try:
        data = await request.json()
        query = data.get("query")
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required.")
        
        if not hasattr(app.state, 'qa_chain'):
            raise HTTPException(status_code=400, detail="Please upload a PDF first.")

        qa_chain = app.state.qa_chain
        response = qa_chain.invoke({"query": query})
        print(response)
        answer = response.get('result', 'No answer found')
        source_documents = response.get('source_documents', [])
        sources = [{"text": doc.page_content} for doc in source_documents]
        
        return {"response": answer, "sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# test
@app.get("/test")
def test_endpoint():
    return {"message": "Test successful"}

# run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
    
# uvicorn pdf_chain:app --reload