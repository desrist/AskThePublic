import os
import pymongo
import requests
import fitz  # PyMuPDF
import tempfile
from pymongo import UpdateOne
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
import logging

database_test = 'test'
database_metadata = 'metadata'
metadata_collection_name = 'feedbackinfo_data'
processeddata_collection_name = 'processed_feedback_data'
# progress_collection_name = 'processing_progress'
progress_collection_name = 'processing_record'

# Initialize OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Missing OpenAI API key")
client = OpenAI(api_key=api_key)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_pdf_to_tempfile(url):
    response = requests.get(url)
    response.raise_for_status()
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_file.write(response.content)
    temp_file.flush()
    temp_file.seek(0)
    logger.info(f"Downloaded PDF to temporary file: {temp_file.name}")
    return temp_file.name

def extract_text_from_pdf(file_path):
    document = fitz.open(file_path)
    text = ""
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
    logger.info(f"Extracted text from PDF: {file_path}")
    return text

def preprocess_text(text):
    preprocessed_text = " ".join(text.replace('\n', ' ').split()).lower()
    return preprocessed_text

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    response = client.embeddings.create(input=[text], model=model)
    embedding = response.data[0].embedding
    logger.info(f"Generated embedding for text: {text[:20]}...")  # Print a preview of the text
    return embedding

def process_feedback(feedback, base_info):
    logger.info(f"Processing feedback ID: {feedback['id']}")
    cleaned_feedback = preprocess_text(feedback.get('feedback', ''))
    if not cleaned_feedback.strip():  # Check if the cleaned feedback is empty
        logger.info(f"Skipping feedback ID: {feedback['id']} because it is empty after preprocessing")
        return None
    
    attachments = feedback.get('attachments', [])
    
    for attachment in attachments:
        if 'links' in attachment:
            pdf_url = attachment['links']
            try:
                pdf_path = download_pdf_to_tempfile(pdf_url)
                pdf_text = extract_text_from_pdf(pdf_path)
                cleaned_pdf_text = preprocess_text(pdf_text)
                cleaned_feedback += f" {cleaned_pdf_text}"
            except Exception as e:
                logger.error(f"Error processing attachment {pdf_url}: {e}")
            finally:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                    logger.info(f"Deleted temporary file: {pdf_path}")
    
    embedding = get_embedding(cleaned_feedback)
    combined = f"Title: {base_info['shortTitle'].strip()}; ID: {base_info['id']}; Content: {cleaned_feedback}; UserType: {feedback.get('userType', '').strip()}; Country: {feedback.get('country', '').strip()}; Organization: {feedback.get('organization', '').strip()}"
    
    cleaned_item = {
        'initiative_id': base_info['id'],
        'feedback_id': feedback['id'],
        'shortTitle': base_info['shortTitle'],
        'topic': base_info['topic'],
        'publicationId': base_info['publicationId'],
        'frontEndStage': base_info['frontEndStage'],
        'totalFeedback': base_info['totalFeedback'],
        'attachments': attachments,
        'language': feedback.get('language', ''),
        'country': feedback.get('country', ''),
        'organization': feedback.get('organization', ''),
        'surname': feedback.get('surname', ''),
        'status': feedback.get('status', ''),
        'firstName': feedback.get('firstName', ''),
        'feedback': cleaned_feedback,
        'dateFeedback': feedback.get('dateFeedback', ''),
        'userType': feedback.get('userType', ''),
        'embedding': embedding,
        'combined': combined
    }
    logger.info(f"Processed feedback ID: {feedback['id']} with combined text")
    return cleaned_item

def process_and_clean_metadata(database, batch_size=2000):
    username = os.getenv('ATLAS_USER')
    password = os.getenv('ATLAS_TOKEN')
    if not username or not password:
        raise ValueError("Missing MongoDB credentials")
    
    uri = f"mongodb+srv://{username}:{password}@cluster0.9tj38oe.mongodb.net/{database}?retryWrites=true&w=majority"
    client = pymongo.MongoClient(uri)
    
    try:
        db = client[database]
        source_collection = db[metadata_collection_name]
        target_collection = db[processeddata_collection_name]
        progress_collection = db[progress_collection_name]
        
        # Create index on the target collection to ensure uniqueness
        target_collection.create_index([('feedback_id', pymongo.ASCENDING)], unique=True)
        
        # Retrieve the list of processed feedback IDs
        processed_ids = set(progress_collection.distinct('feedback_id'))
        logger.info(f"Retrieved {len(processed_ids)} processed IDs")

        cursor = source_collection.find()
        
        operations = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for item in cursor:
                base_info = {
                    'id': item['id'],
                    'shortTitle': item['shortTitle'],
                    'topic': item['topic'],
                    'publicationId': item['publicationId'],
                    'frontEndStage': item['frontEndStage'],
                    'totalFeedback': item['totalFeedback']
                }
                
                feedbacks = item.get('feedback', [])
                for feedback in feedbacks:
                    if isinstance(feedback, dict) and feedback['id'] not in processed_ids:
                        logger.info(f"Processing feedback ID: {feedback['id']}")
                        futures.append(executor.submit(process_feedback, feedback, base_info))
                    else:
                        logger.info(f"Skipping feedback as it's already processed or not a dictionary")
            
            for future in as_completed(futures):
                try:
                    cleaned_item = future.result()
                    if cleaned_item is None:
                        continue  # Skip items that were filtered out

                    operations.append(UpdateOne(
                        {'feedback_id': cleaned_item['feedback_id']},
                        {'$set': cleaned_item},
                        upsert=True
                    ))
                    
                    # update the database in batches
                    if len(operations) >= batch_size:
                        target_collection.bulk_write(operations)
                        logger.info("Batch update completed")
                        operations = []
                    
                    # Update the progress
                    last_processed_id = cleaned_item['feedback_id']
                    progress_collection.update_one(
                        {'feedback_id': last_processed_id},
                        {"$set": {'feedback_id': last_processed_id}},
                        upsert=True
                    )
                    logger.info(f"Updated progress with last processed ID: {last_processed_id}")
                except Exception as e:
                    logger.error(f"Error in processing feedback: {e}")
        
        # update the remaining documents
        if operations:
            target_collection.bulk_write(operations)
            logger.info("Final batch update completed")
        
        logger.info("Data cleaning completed")
    
    finally:
        client.close()
        logger.info("Database connection closed")


# import os
# import pymongo
# import requests
# import fitz  # PyMuPDF
# import tempfile
# from pymongo import UpdateOne
# from concurrent.futures import ThreadPoolExecutor, as_completed
# import logging
# import json
# import pandas as pd
# import time
# from openai import OpenAI

# database_test = 'test'
# metadata_collection_name = 'feedbackinfo_data'
# processeddata_collection_name = 'processed_feedback_data'
# progress_collection_name = 'processing_progress'

# # Initialize OpenAI API key
# api_key = os.getenv("OPENAI_API_KEY")
# if not api_key:
#     raise ValueError("Missing OpenAI API key")
# client = OpenAI(api_key=api_key)

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# def download_pdf_to_tempfile(url):
#     response = requests.get(url)
#     response.raise_for_status()
#     temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
#     temp_file.write(response.content)
#     temp_file.flush()
#     temp_file.seek(0)
#     logger.info(f"Downloaded PDF to temporary file: {temp_file.name}")
#     return temp_file.name

# def extract_text_from_pdf(file_path):
#     document = fitz.open(file_path)
#     text = ""
#     for page_num in range(len(document)):
#         page = document.load_page(page_num)
#         text += page.get_text()
#     logger.info(f"Extracted text from PDF: {file_path}")
#     return text

# def preprocess_text(text):
#     preprocessed_text = " ".join(text.replace('\n', ' ').split()).lower()
#     return preprocessed_text

# def process_feedback(feedback, base_info):
#     logger.info(f"Processing feedback ID: {feedback['id']}")
#     cleaned_feedback = preprocess_text(feedback.get('feedback', ''))
#     if not cleaned_feedback.strip():  # Check if the cleaned feedback is empty
#         logger.info(f"Skipping feedback ID: {feedback['id']} because it is empty after preprocessing")
#         return None
    
#     attachments = feedback.get('attachments', [])
    
#     for attachment in attachments:
#         if 'links' in attachment:
#             pdf_url = attachment['links']
#             try:
#                 pdf_path = download_pdf_to_tempfile(pdf_url)
#                 pdf_text = extract_text_from_pdf(pdf_path)
#                 cleaned_pdf_text = preprocess_text(pdf_text)
#                 cleaned_feedback += f" {cleaned_pdf_text}"
#             except Exception as e:
#                 logger.error(f"Error processing attachment {pdf_url}: {e}")
#             finally:
#                 if os.path.exists(pdf_path):
#                     os.remove(pdf_path)
#                     logger.info(f"Deleted temporary file: {pdf_path}")
    
#     combined = f"Title: {base_info['shortTitle'].strip()}; Content: {cleaned_feedback}; UserType: {feedback.get('userType', '').strip()}; Country: {feedback.get('country', '').strip()}; Organization: {feedback.get('organization', '').strip()}"
    
#     cleaned_item = {
#         'feedback_id': feedback['id'],
#         'shortTitle': base_info['shortTitle'],
#         'topic': base_info['topic'],
#         'publicationId': base_info['publicationId'],
#         'frontEndStage': base_info['frontEndStage'],
#         'totalFeedback': base_info['totalFeedback'],
#         'attachments': attachments,
#         'language': feedback.get('language', ''),
#         'country': feedback.get('country', ''),
#         'organization': feedback.get('organization', ''),
#         'surname': feedback.get('surname', ''),
#         'status': feedback.get('status', ''),
#         'firstName': feedback.get('firstName', ''),
#         'feedback': cleaned_feedback,
#         'dateFeedback': feedback.get('dateFeedback', ''),
#         'userType': feedback.get('userType', ''),
#         'combined': combined
#     }
#     logger.info(f"Processed feedback ID: {feedback['id']} with combined text")
#     return cleaned_item

# def create_jsonl_file_for_batch(processed_feedbacks, batch_index, output_folder):
#     check_and_create_folder(output_folder)
#     output_file = os.path.join(output_folder, f'processed_feedback_batch_part{batch_index}.jsonl')
#     if os.path.exists(output_file):
#         os.remove(output_file)
    
#     with open(output_file, 'a') as file:
#         for feedback in processed_feedbacks:
#             payload = {
#                 "custom_id": f"custom_id_{feedback['feedback_id']}",
#                 "method": "POST",
#                 "url": "/v1/embeddings",
#                 "body": {
#                     "input": feedback["combined"],
#                     "model": "text-embedding-3-small",
#                     "encoding_format": "float",
#                     'dimensions': 1536
#                 }
#             }
#             file.write(json.dumps(payload) + '\n')
    
#     return output_file

# def check_and_create_folder(folder_path):
#     if not os.path.exists(folder_path):
#         os.makedirs(folder_path)
#         logger.info(f"Folder '{folder_path}' created.")
#     else:
#         logger.info(f"Folder '{folder_path}' already exists.")

# def create_and_run_batch_job(jsonl_file):
#     file_id = client.files.create(file=open(jsonl_file, "rb"), purpose="batch").id
#     job = client.batches.create(input_file_id=file_id, endpoint="/v1/embeddings", completion_window="24h")
#     return job.id

# def monitor_batch_job(job_id):
#     while True:
#         job = client.batches.retrieve(job_id)
#         if job.status == "failed":
#             logger.error(f"Job {job_id} has failed with error {job.errors}")
#             return None
#         elif job.status == 'in_progress':
#             logger.info(f'Job {job_id} is in progress, {job.request_counts.completed}/{job.request_counts.total} requests completed')
#         elif job.status == 'finalizing':
#             logger.info(f'Job {job_id} is finalizing, waiting for the output file id')
#         elif job.status == "completed":
#             logger.info(f"Job {job_id} has finished")
#             return job.output_file_id
#         else:
#             logger.info(f'Job {job_id} is in status {job.status}')
#         time.sleep(600)

# def extract_embeddings_from_output_file(output_file_id):
#     output_file = client.files.content(output_file_id).text
#     embedding_results = []
#     for line in output_file.split('\n')[:-1]:
#         data = json.loads(line)
#         custom_id = data.get('custom_id')
#         embedding = data['response']['body']['data'][0]['embedding']
#         embedding_results.append([custom_id, embedding])
#     return embedding_results

# def update_embeddings_in_mongo(db, embedding_results):
#     target_collection = db[processeddata_collection_name]
#     for custom_id, embedding in embedding_results:
#         feedback_id = int(custom_id.split('custom_id_')[1])
#         target_collection.update_one(
#             {'feedback_id': feedback_id},
#             {'$set': {'embedding': embedding}}
#         )
#     logger.info("Updated embeddings in MongoDB")

# def process_and_clean_metadata(database, batch_size=20):
#     username = os.getenv('ATLAS_USER')
#     password = os.getenv('ATLAS_TOKEN')
#     if not username or not password:
#         raise ValueError("Missing MongoDB credentials")
    
#     uri = f"mongodb+srv://{username}:{password}@cluster0.9tj38oe.mongodb.net/{database}?retryWrites=true&w=majority"
#     client = pymongo.MongoClient(uri)
    
#     try:
#         db = client[database]
#         source_collection = db[metadata_collection_name]
#         target_collection = db[processeddata_collection_name]
#         progress_collection = db[progress_collection_name]
        
#         # Create index on the target collection to ensure uniqueness
#         target_collection.create_index([('feedback_id', pymongo.ASCENDING)], unique=True)
        
#         # Retrieve the list of processed feedback IDs
#         processed_ids = set(progress_collection.distinct('feedback_id'))
#         logger.info(f"Retrieved {len(processed_ids)} processed IDs")

#         cursor = source_collection.find()
        
#         processed_feedbacks = []
#         batch_index = 0
        
#         with ThreadPoolExecutor(max_workers=10) as executor:
#             futures = []
#             for item in cursor:
#                 base_info = {
#                     'id': item['id'],
#                     'shortTitle': item['shortTitle'],
#                     'topic': item['topic'],
#                     'publicationId': item['publicationId'],
#                     'frontEndStage': item['frontEndStage'],
#                     'totalFeedback': item['totalFeedback']
#                 }
                
#                 feedbacks = item.get('feedback', [])
#                 for feedback in feedbacks:
#                     if isinstance(feedback, dict) and feedback['id'] not in processed_ids:
#                         futures.append(executor.submit(process_feedback, feedback, base_info))
            
#             for future in as_completed(futures):
#                 try:
#                     cleaned_item = future.result()
#                     if cleaned_item is None:
#                         continue  # Skip items that were filtered out
#                     processed_feedbacks.append(cleaned_item)
                    
#                     if len(processed_feedbacks) >= batch_size:
#                         jsonl_file = create_jsonl_file_for_batch(processed_feedbacks, batch_index, './batch_files')
#                         job_id = create_and_run_batch_job(jsonl_file)
#                         output_file_id = monitor_batch_job(job_id)
#                         if output_file_id:
#                             embedding_results = extract_embeddings_from_output_file(output_file_id)
#                             update_embeddings_in_mongo(db, embedding_results)
                        
#                         # Delete the JSONL file after processing
#                         os.remove(jsonl_file)
#                         logger.info(f"Deleted JSONL file: {jsonl_file}")
                        
#                         processed_feedbacks = []
#                         batch_index += 1
                        
#                 except Exception as e:
#                     logger.error(f"Error in processing feedback: {e}")
        
#         # Process any remaining feedbacks
#         if processed_feedbacks:
#             jsonl_file = create_jsonl_file_for_batch(processed_feedbacks, batch_index, './batch_files')
#             job_id = create_and_run_batch_job(jsonl_file)
#             output_file_id = monitor_batch_job(job_id)
#             if output_file_id:
#                 embedding_results = extract_embeddings_from_output_file(output_file_id)
#                 update_embeddings_in_mongo(db, embedding_results)
            
#             # Delete the JSONL file after processing
#             os.remove(jsonl_file)
#             logger.info(f"Deleted JSONL file: {jsonl_file}")
        
#         logger.info("Data cleaning completed")
    
#     finally:
#         client.close()
#         logger.info("Database connection closed")

