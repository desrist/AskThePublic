from openai import OpenAI
import os

api_key = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

def get_embedding_dimensions(text, model="text-embedding-3-small"):
    response = client.embeddings.create(input=[text], model=model)
    embedding = response.data[0].embedding
    return len(embedding)

# test
text = "Hello, world!"
dimensions = get_embedding_dimensions(text)
print(f"The dimension of the embedding vector is: {dimensions}")
