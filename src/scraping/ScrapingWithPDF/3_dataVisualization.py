import asyncio
import aiohttp
import pymongo
import os
from pymongo import UpdateOne
from aiohttp.client_exceptions import ClientOSError

# Database and collection names
database_metadata = 'metadata'
metadata_collection_name = 'feedbackinfo_data'
processeddata_collection_name = 'processed_feedback_data'
progress_collection_name = 'processing_record'

# Collection for keywords search
keywords_collection_name = 'keywords_search_data'
# Collection for initiatives summary
initiatives_summary_collection_name = 'initiatives_summary_data'

# MongoDB credentials from environment variables
username = os.getenv('ATLAS_USER')
password = os.getenv('ATLAS_TOKEN')
if not username or not password:
    raise ValueError("Missing MongoDB credentials")

# MongoDB connection URI and client setup
uri = f"mongodb+srv://{username}:{password}@cluster0.9tj38oe.mongodb.net/{database_metadata}?retryWrites=true&w=majority"
client = pymongo.MongoClient(uri)

# Database and collection objects
db = client[database_metadata]
feedbackinfo_collection = db[metadata_collection_name]
keywords_search_collection = db[keywords_collection_name]
initiatives_summary_collection = db[initiatives_summary_collection_name]

# Function to create and update keywords collection
def create_and_update_keywords_collection():
    feedbackinfo_data = feedbackinfo_collection.find({}, {"_id": 1, "id": 1, "shortTitle": 1, "topic": 1, "totalFeedback": 1})

    operations = []
    seen_ids = set()
    
    for document in feedbackinfo_data:
        document_id_str = str(document["id"])
        
        if document_id_str in seen_ids:
            continue  # Skip if we've already processed this ID
        
        seen_ids.add(document_id_str)
        
        link = f"https://ec.europa.eu/info/law/better-regulation/have-your-say/initiatives/{document['id']}"
        
        document_totalFeedback_str = str(document["totalFeedback"])
        
        # Update the keywords collection
        operations.append(
            UpdateOne(
                {"_id": document["_id"]},
                {
                    "$set": {
                        "id": document_id_str, 
                        "shortTitle": document["shortTitle"],
                        "topic": document["topic"],
                        "totalFeedback": document_totalFeedback_str,
                        "links": link
                    }
                },
                upsert=True
            )
        )
    
    if operations:
        result = keywords_search_collection.bulk_write(operations)
        print(f"Matched: {result.matched_count}, Modified: {result.modified_count}, Upserted: {result.upserted_count}")

# Asynchronous fetch function to get data from API
async def fetch_data(session, url, params=None, semaphore=None, timeout=10):
    async with semaphore:
        try:
            async with session.get(url, params=params, timeout=timeout) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Error: {response.status} for URL: {url}")
                    return 'no data'
        except asyncio.TimeoutError:
            print(f"TimeoutError for URL: {url}")
            return 'no data'
        except ClientOSError:
            print(f"ClientOSError for URL: {url}")
            return 'no data'

# Process each initiative to get attachments and save to MongoDB
async def process_initiative(session, semaphore, initiative_id, short_title):
    base_url = f"https://ec.europa.eu/info/law/better-regulation/brpapi/groupInitiatives/{initiative_id}"
    data = await fetch_data(session, base_url, semaphore=semaphore)
    
    if data == 'no data':
        return None
    
    attachments_info = []
    
    for publication in data.get('publications', []):
        if not publication.get('attachments'):
            continue
        
        for attachment in publication['attachments']:
            if attachment.get('language') == 'EN':
                document_id = attachment.get('documentId')
                download_url = f"https://ec.europa.eu/info/law/better-regulation/api/download/{document_id}"
                attachment_title = attachment.get('title', 'No title')  # Get the title, default to 'No title' if missing
                attachments_info.append({
                    "documentId": document_id,
                    "downloadUrl": download_url,
                    "title": attachment_title  # Add title to the saved data
                })
    
    # Save results to MongoDB
    if attachments_info:
        initiatives_summary_collection.update_one(
            {"initiative_id": initiative_id},
            {
                "$set": {
                    "initiative_id": initiative_id,
                    "shortTitle": short_title,
                    "attachments": attachments_info
                }
            },
            upsert=True
        )
        print(f"Saved data for initiative {initiative_id}")


# Main async function to fetch and process data for all initiatives
async def fetch_all_initiatives():
    # Fetch all initiative IDs from keywords_search_collection
    initiative_ids = keywords_search_collection.find({}, {"id": 1, "shortTitle": 1})
    
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(10)  # Limit concurrent requests
        
        tasks = []
        for initiative in initiative_ids:
            initiative_id = initiative['id']
            short_title = initiative.get('shortTitle', '')
            tasks.append(process_initiative(session, semaphore, initiative_id, short_title))
        
        await asyncio.gather(*tasks)

# Main function to run both the synchronous and asynchronous parts
def main():
    # First, update the keywords collection
    create_and_update_keywords_collection()
    
    # Then, asynchronously fetch all initiatives
    asyncio.run(fetch_all_initiatives())

if __name__ == "__main__":
    main()
