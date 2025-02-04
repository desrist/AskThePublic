import os
import pandas as pd
import tiktoken
from openai import OpenAI
from dotenv import load_dotenv
import time
import json

# load csv
def load_data(file_path):
    df = pd.read_csv(file_path)
    df = df.dropna()
    return df

# create a combined column with column "short_title" "feedback_content" "user_type" "country"
def create_combined_column(df):
    df["combined"] = (
        "Title: " + df.short_title.str.strip() +
        "; Content: " + df.feedback_content.str.strip() +
        "; UserType: " + df.user_type.str.strip() +
        "; Country: " + df.country.str.strip()
    )
    return df

# filter out long texts that over model capacity
def filter_long_texts(df, max_tokens, encoding):
    df["n_tokens"] = df.combined.apply(lambda x: len(encoding.encode(x)))
    df = df[df.n_tokens <= max_tokens]
    return df

# use openai embedding API to get embedding for each row
def get_embedding(client, text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

# process data in batches
def process_batches(df, client, batch_size):
    df_batches = [df[i:i+batch_size] for i in range(0, df.shape[0], batch_size)]
    all_data = []

    for batch in df_batches:
        for _, row in batch.iterrows():
            embedding = get_embedding(client, row['combined'])
            row_data = row.to_dict()
            row_data["embedding"] = embedding
            all_data.append(row_data)
            print(f"Processed {len(all_data)} rows")
    
    return all_data

if __name__ == '__main__':
    load_dotenv()
    api_key = os.environ["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)

    topic = 'AGRI'
    SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    processed_file_path = os.path.join(SRC_DIR, 'data', topic, 'processed_data.csv')
    output_path = os.path.join(SRC_DIR, 'data', topic, 'embedded_data.csv')

    df = load_data(processed_file_path)
    df = create_combined_column(df)

    # filter long texts
    max_tokens = 4000 # default is 8192
    embedding_encoding = "cl100k_base"
    encoding = tiktoken.get_encoding(embedding_encoding)
    df = filter_long_texts(df, max_tokens, encoding)

    # generate embedding for each row
    start_time = time.time()
    batch_size = 100
    all_data = process_batches(df, client, batch_size)
    print(f"Processed {len(all_data)} rows in {time.time() - start_time} seconds")

    # save to csv
    output_df = pd.DataFrame(all_data)
    output_df["embedding"] = output_df["embedding"].apply(json.dumps)
    output_df.to_csv(output_path, index=False)

    print("Embedding generation and saving to local file completed.")