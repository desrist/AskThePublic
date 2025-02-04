import json 
import pymongo
import os 
import pandas as pd
from dotenv import load_dotenv

def str_to_list(collection):
    for document in collection.find({}):
        if isinstance(document['embedding'], str):
            embedding = json.loads(document['embedding'])
            collection.update_one({'_id': document['_id']}, {'$set': {'embedding': embedding}})

    print("Completed updating embeddings.")
    
def import_data_to_mongodb(file_path, collection):
    if file_path.endswith('.csv'):
        data = pd.read_csv(file_path)
        data_dict = data.to_dict(orient='records')
        collection.insert_many(data_dict)
    elif file_path.endswith('.json'):
        with open(file_path, 'r') as f:
            data = json.load(f)
        collection.insert_many(data)
    else:
        raise ValueError("Unsupported file format")
    
def main():
    load_dotenv()
    topic = 'AGRI'
    SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    file_path = os.path.join(SRC_DIR, 'data', topic, 'embedded_data.csv')
    username = os.getenv('ATLAS_USER')
    password = os.getenv('ATLAS_TOKEN')

    uri = f"mongodb+srv://{username}:{password}@cluster0.9tj38oe.mongodb.net/<database>?retryWrites=true&w=majority"
    client = pymongo.MongoClient(uri)
    db = client['citizen_feedback']
    collection = db['AGRI_embedded_data']

    try:
        import_data_to_mongodb(file_path, collection)
        str_to_list(collection)
        print('Data import and update completed successfully.')
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()