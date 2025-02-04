# scraping data by initiatives topics.
async def fetch_data(session, url, params=None, semaphore=None, timeout=10):
    async with semaphore:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f'Error: {response.status} for URL: {url}')
                    return 'no data'
        except asyncio.TimeoutError:
            print(f'TimeoutError for URL: {url}')
            return 'no data'
        except ClientOSError:
            print(f'ClientOSError for URL: {url}')
            return 'no data'

# Pipline 1: get initiatives id
async def get_init_id(topic, size, language, concurrency=5):
    start_time = time.time()
    output_path = os.path.join(SRC_DIR, 'data', topic)
    file_path = os.path.join(output_path, 'initiatives_id.json')
    
    # return list of ids if file exists
    if os.path.exists(file_path):
        print(f'{file_path} already exists, skipping get_init_id.')
        with open(file_path, 'r', encoding='utf-8') as f:
            info = json.load(f)
        id_list = [item['id'] for item in info]
        return id_list

    page = 0
    info = []
    id_list = []
    total_pages = None
    url = config['urls']['initiatives_id']
    params = {
        'topic': topic,
        'size': size,
        'language': language,
        'page': page
    }
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        
    # set up semaphore to limit concurrency
    semaphore = asyncio.Semaphore(concurrency)
    # set up retry client with exponential backoff
    retry_options = ExponentialRetry(attempts=5)
    
    # run the fetch_data function with the retry client
    async with RetryClient(raise_for_status=False, retry_options=retry_options) as session:
        while True:
            params['page'] = page  # update page number
            data = await fetch_data(session, url, params, semaphore)
            if data == 'no data':
                break
            if data is None:
                break
            initiatives_data = data.get('_embedded', {}).get('initiativeResultDtoes', [])
            for item in initiatives_data:
                id = int(item.get('id'))
                status = item.get('initiativeStatus')
                short_title = item.get('shortTitle')
                info.append({'id': id, 'status': status, 'short_title': short_title})
                id_list.append(id)
                print(f'{id} success')
            if total_pages is None:
                total_pages = data.get('page', {}).get('totalPages', 0)

            if page >= total_pages:
                break
            page += 1
            print("page:", page)
            await asyncio.sleep(0.3)  # wait for a short time before the next request

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=4)
        print(f'{topic} initiatives_id.json successfully processed')
        
    end_time = time.time()
    print(f'{topic} initiatives_id.json processing time: {end_time - start_time} seconds')
    return id_list

# Pipline 2: get publication id
async def get_publication_id(id_list, topic, concurrency=5):
    start_time = time.time()
    output_path = os.path.join(SRC_DIR, 'data', topic)
    file_path = os.path.join(output_path, 'p_id.json')
    
    if os.path.exists(file_path):
        print(f'{file_path} already exists, skipping get_publication_id.')
        with open(file_path, 'r', encoding='utf-8') as f:
            info_big = json.load(f)
        pubid = [{'id': item['id'], 'publicationId': [pub['publicationId'] for pub in item['info']], 'frontEndStage': [pub['frontEndStage'] for pub in item['info']], 'totalFeedback': [pub['total_Feedback'] for pub in item['info']]} for item in info_big]
        return pubid

    info_big = []
    pubid = []

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    semaphore = asyncio.Semaphore(concurrency)
    retry_options = ExponentialRetry(attempts=5)

    async with RetryClient(raise_for_status=False, retry_options=retry_options) as session:
        tasks = []
        for id in id_list:
            p_id_url = config['urls']['publication_id']
            url = p_id_url + f'{id}'
            tasks.append(fetch_data(session, url, semaphore=semaphore))

        responses = await asyncio.gather(*tasks)
        for id, data in zip(id_list, responses):
            if data is None:
                continue
            publications_data = data.get('publications', [])
            info_small = []
            publication_ids = []
            frontendstage = []
            totalFeedback = []
            for item in publications_data:
                publi_id = item.get('id')
                title = item.get('title')
                type = item.get('type')
                stage = item.get('stage')
                total_Feedback = item.get('totalFeedback')
                groupId = item.get('groupId')
                frontEndStage = item.get('frontEndStage')
                createdDate = item.get('createdDate')
                publishedDate = item.get('publishedDate')
                endDate = item.get('endDate')
                info_small.append({
                    'publicationId': publi_id, 'title': title, 'type': type, 'stage': stage, 'total_Feedback': total_Feedback,
                    'groupId': groupId, 'frontEndStage': frontEndStage, 'createdDate': createdDate,
                    'publishedDate': publishedDate, 'endDate': endDate
                })
                publication_ids.append(publi_id)
                frontendstage.append(frontEndStage)
                totalFeedback.append(total_Feedback)
            info_big.append({'id': id, 'info': info_small})
            # use totalFeedback to filter out initiatives with no feedback in next steps
            pubid.append({'id': id, 'publicationId': publication_ids, 'frontEndStage': frontendstage, 'totalFeedback': totalFeedback})
            print(f'{id} done')
            await asyncio.sleep(0.3)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(info_big, f, ensure_ascii=False, indent=4)
        print(f'{topic} p_id.json successfully processed')

    end_time = time.time()
    print(f'{topic} p_id.json processing time: {end_time - start_time} seconds')
    return pubid

# Pipline3: get feedback information
async def get_feedback_info(pubid, topic, concurrency=5):
    start_time = time.time()
    output_path = os.path.join(SRC_DIR, 'data', topic)
    final_file = os.path.join(output_path, 'feedback_info.json')
    
    if os.path.exists(final_file):
        print(f'{final_file} already exists, skipping get_feedback_info.')
        return

    feedback_info = []

    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    semaphore = asyncio.Semaphore(concurrency)
    feedback_info_url = config['urls']['feedback_info']
    
    retry_options = ExponentialRetry(attempts=3)
    
    async with RetryClient(raise_for_status=False, retry_options=retry_options) as session:
        for item in pubid:
            id = item['id']
            publicationId = item['publicationId']
            frontendstage = item['frontEndStage']
            totalFeedback = item['totalFeedback']
            for i, pub_id in enumerate(publicationId):
                # set a threshold for the number of feedbacks
                if totalFeedback[i] == 0 or totalFeedback[i] > 2000:
                    new_dic = {
                        'id': id,
                        'publicationId': pub_id,
                        'frontEndStage': frontendstage[i],
                        'feedback': 'no data'
                    }
                    feedback_info.append(new_dic)
                    print(f'{id} {pub_id} {frontendstage[i]} skipped due to zero feedback')
                    continue
                
                page_number = 0
                # get feedback information,depends on situation
                while True:
                    url = feedback_info_url.format(pub_id, page_number)
                    data = await fetch_data(session, url, semaphore=semaphore)
                    if data == 'no data':
                        new_dic = {
                            'id': id,
                            'publicationId': pub_id,
                            'frontEndStage': frontendstage[i],
                            'feedback': 'no data'
                        }
                        feedback_info.append(new_dic)
                        break
                    elif data:
                        feedback_embedded = data.get('_embedded', {}).get('feedback', [])
                        if not feedback_embedded:
                            break
                        feedback_content = feedback_embedded[0].get("feedback", None)

                        if feedback_content is None:
                            new_dic = {
                                'id': id,
                                'publicationId': pub_id,
                                'frontEndStage': frontendstage[i],
                                'feedback': 'no data'
                            }
                            feedback_info.append(new_dic)
                            break

                        new_dic = {
                            'id': id,
                            'publicationId': pub_id,
                            'frontEndStage': frontendstage[i],
                            'feedback': data
                        }
                        feedback_info.append(new_dic)

                        total_page = data.get('page', {}).get('totalPages', 0)
                        if page_number > total_page - 1:
                            break
                        page_number += 1
                    else:
                        break
                    await asyncio.sleep(0.3)
                
            print(f'{id} {pub_id} {frontendstage[i]} done')
                    
    with open(final_file, 'w', encoding='utf-8') as f:
        json.dump(feedback_info, f, ensure_ascii=False, indent=4)
    end_time = time.time()
    print(f'Total time for {topic}: {end_time - start_time:.2f} seconds')
    return feedback_info


async def main(topic_list):
    start_time = time.time()
    for topic in topic_list:
        # get initiatives id
        initiatives_id = await get_init_id(topic, size=10, language='en', concurrency=5)
        
        # get publication ids
        publication_ids = await get_publication_id(initiatives_id, topic, concurrency=5)
        
        # get feedback info
        await get_feedback_info(publication_ids, topic, concurrency=5)
    end_time = time.time()
    print(f'Total time: {end_time - start_time}')
    
if __name__ == "__main__":
    import sys
    import os
    import requests
    import time
    import json
    import aiohttp
    import asyncio
    from aiohttp_retry import RetryClient, ExponentialRetry
    from aiohttp.client_exceptions import ClientOSError
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    sys.path.append(project_root)
    from configLoader import config
    
    SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    topic_list = config['topics']
    asyncio.run(main(topic_list))