from pymongo import MongoClient
import os
import dotenv

dotenv.load_dotenv()

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
collection = client[db_name][collection_name]
pipeline = [
    {"$group": {"_id": "$userType", "count": {"$sum": 1}}}
]

user_types = collection.aggregate(pipeline)

for user_type in user_types:
    print(f"UserType: {user_type['_id']}, Count: {user_type['count']}")