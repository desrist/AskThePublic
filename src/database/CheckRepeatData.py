from pymongo import MongoClient
from collections import Counter
import dotenv
import os

dotenv.load_dotenv()
# Get MongoDB Atlas credentials from environment variables
ATLAS_TOKEN = os.environ["ATLAS_TOKEN"]
ATLAS_USER = os.environ["ATLAS_USER"]
# Initialize MongoDB Connection
client = MongoClient(
    "mongodb+srv://{}:{}@cluster0.9tj38oe.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0".format(
            ATLAS_USER, ATLAS_TOKEN)
)
db = client["metadata"]
collection = db['feedbackinfo_data']

all_ids = collection.find({}, {'id': 1})

id_list = [doc.get('id') for doc in all_ids if 'id' in doc]

id_count = Counter(id_list)

duplicate_ids = [id for id, count in id_count.items() if count > 1]

print("repeat id:", duplicate_ids)
