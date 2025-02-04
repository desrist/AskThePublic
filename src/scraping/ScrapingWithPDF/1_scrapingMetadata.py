# 1_scrapingMetadata.py 
# scraping data from website and store metadata to mongodb atalas

import os
import json
import asyncio
import time
import pandas as pd
from utilsScraping import get_init_id, get_publication_id, get_feedback_info, convert_objectid_to_str
from aiohttp_retry import RetryClient, ExponentialRetry

topic_dict = {
    "AGRI": "Agriculture and rural development",
    "FINANCE": "Banking and financial services",
    "BORDERS": "Borders and security",
    "BUDGET": "Budget",
    "BUSINESS": "Business and industry",
    "CLIMA": "Climate action",
    "COMP": "Competition",
    "CONSUM": "Consumers",
    "CULT": "Culture and media",
    "CUSTOMS": "Customs",
    "DIGITAL": "Digital economy and society",
    "ECFIN": "Economy, finance and the euro",
    "EAC": "Education and training",
    "EMPL": "Employment and social affairs",
    "ENER": "Energy",
    "ENV": "Environment",
    "ENLARG": "EU enlargement",
    "NEIGHBOUR": "European neighbourhood policy",
    "FOOD": "Food safety",
    "FOREIGN": "Foreign affairs and security policy",
    "FRAUD": "Fraud prevention",
    "HOME": "Home affairs",
    "HUMAN": "Humanitarian aid and civil protection",
    "INST": "Institutional affairs",
    "INTDEV": "International cooperation and development",
    "JUST": "Justice and fundamental rights",
    "MARE": "Maritime affairs and fisheries",
    "ASYL": "Migration and asylum",
    "HEALTH": "Public health",
    "REGIO": "Regional policy",
    "RESEARCH": "Research and innovation",
    "SINGMARK": "Single market",
    "SPORT": "Sport",
    "STAT": "Statistics",
    "TAX": "Taxation",
    "TRADE": "Trade",
    "TRANSPORT": "Transport",
    "YOUTH": "Youth"
}

async def main():
    
    topic_list = list(topic_dict.keys()) # use all topics
    # topic_list = ['AGRI']
    total_feedback = []
    all_data = []  # store all data

    for topic in topic_list:
        start_time = time.time()
        page = 0

        semaphore = asyncio.Semaphore(10)
        retry_options = ExponentialRetry(attempts=5)
        
        async with RetryClient(raise_for_status=False, retry_options=retry_options) as session:
            while True:
                print(f'Processing page {page} for topic {topic}')
                id_list, total_pages = await get_init_id(session, topic, size=10, language='en', page=page, semaphore=semaphore)
                if not id_list:
                    break
                pubid = await get_publication_id(session, id_list, semaphore)
                feedback_info = await get_feedback_info(session, pubid, topic, semaphore)
                # Convert ObjectId to string before saving to JSON
                feedback_info_str = convert_objectid_to_str(feedback_info)
                if page >= total_pages - 1:
                    break
                page += 1
        
                total_feedback.extend(feedback_info_str)
                all_data.extend(feedback_info_str)
        
    #     output = 'D:/visualstudiocode/project/eufeedbackapp/src/database/test_data'
    #     final_file = os.path.join(output, f'test_data.json')
    #     if not os.path.exists(output):
    #         os.makedirs(output)
        
    #     with open(final_file, 'w', encoding='utf-8') as f:
    #         json.dump(total_feedback, f, ensure_ascii=False, indent=4)
        
    #     end_time = time.time()
    #     print(f'Total processing time for topic {topic}: {end_time - start_time} seconds')

    # # save all to csv
    # df = pd.DataFrame(all_data)
    # csv_output = os.path.join(output, 'all_topics_data.csv')
    # df.to_csv(csv_output, index=False)
    # print(f"All topics data saved to {csv_output}")

if __name__ == '__main__':
    asyncio.run(main())