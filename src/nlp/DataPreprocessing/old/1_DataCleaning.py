# final version of data: Id, shorttitle, country, language, feedback
import os
import json
import pandas as pd
import sys

src_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
print(src_root)
sys.path.append(src_root)
from configLoader import config

def load_data(file_path, file_name):
    full_path = os.path.join(file_path, file_name)
    if not os.path.exists(full_path):
        print(f"File '{file_name}' does not exist.")
        return None   
    with open(full_path, 'r', encoding='utf-8') as file:
        return json.load(file)
    
def filter_feedback(data):
    return [item for item in data if item.get("feedback") != "no data"]

# merge data from 'initiatives_id.json' and 'feedback_info.json'
def merge_data(initiatives, feedbacks):
    
    # merge feedbacks with the same initiative id
    feedback_dict = {}
    for item in feedbacks:
        id = item['id']
        if id in feedback_dict:
            feedback_dict[id].append(item)
        else:
            feedback_dict[id] = [item]
            
    # merge initiatives and feedbacks 
    merged_data = []
    for initiative in initiatives:
        feedback_items = feedback_dict.get(initiative["id"], [])
        for feedback_item in feedback_items:
            for feedback in feedback_item["feedback"]["_embedded"]["feedback"]:
                # filter feedback content length >= 100
                feedback_content = feedback.get("feedback")
                if feedback_content and (4000 > len(feedback_content) >= 100) :
                    merged_item = {
                        "id": initiative["id"],
                        "short_title": initiative["short_title"],
                        "feedback_content": feedback_content,
                        "feedback_id": feedback.get("id"),
                        "country": feedback.get("country"),
                        "language": feedback.get("language"),
                        "feedback_date": feedback.get("dateFeedback"),
                        "user_type": feedback.get("userType"),
                    }
                    merged_data.append(merged_item)
    return merged_data
    
def data_preprocessing(data):

    df = pd.DataFrame(data)
    # delete feedback = null
    df = df[df['feedback_content'].notnull()]
    # lower, remove /n
    if 'feedback_content' in df.columns:
        df['feedback_content'] = df['feedback_content'].apply(lambda x: " ".join(x.replace('\n', ' ').split()).lower())
    # delete same data
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

if __name__ == '__main__':
    topic_list = config.get('topics')
    print(topic_list)
    for topic in topic_list:
        print(f'Processing topic: {topic}')
        data_dir = os.path.join(src_root, 'data', topic)
        
        # Load data
        initiatives = load_data(data_dir, 'initiatives_id.json')
        feedback_info = load_data(data_dir, 'feedback_info.json')

        # Filter and merge data
        filtered_feedback = filter_feedback(feedback_info)
        merged_data = merge_data(initiatives, filtered_feedback)

        # Preprocess data
        final_df = data_preprocessing(merged_data)
        print(final_df.head())

        # Save processed data to a new file
        output_path = os.path.join(data_dir, 'processed_data.csv')
        final_df.to_csv(output_path, index=False)
    
    
    