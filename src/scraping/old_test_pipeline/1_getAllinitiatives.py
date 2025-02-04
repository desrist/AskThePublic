'''
initiatives id url = 'https://ec.europa.eu/info/law/better-regulation/brpapi/searchInitiatives?topic=AGRI&size=10&language=EN' 
e.g. topic = 'AGRI' (Agriculture and rural development) size, page

get initiative id and title

Pid url = 'https://ec.europa.eu/info/law/better-regulation/brpapi/groupInitiatives/{initative_id}'

get p_id, totalfeedback, type, ...

feedback url = 'https://ec.europa.eu/info/law/better-regulation/api/allFeedback?publicationId={publication_id}&keywords=&language=EN&page=0&size=10&sort=dateFeedback,DESC'

pdf url = 'https://ec.europa.eu/info/law/better-regulation/api/download/{documentId}'
'''

import requests
import json
import os
import time

def get_init_id(url, topic, size, language):
    page = 0
    info = []
    total_pages = None
    time_period = 1
    output_path = os.path.join(SRC_DIR, 'data', topic)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    while True:
        params = {
            'topic': topic,
            'size': size,
            'page': page,
            'language': language,
            
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print('Error:', response.status_code)
            break
        data = response.json()
        initiatives_data = data.get('_embedded', {}).get('initiativeResultDtoes', [])
        for item in initiatives_data:
            id = int(item.get('id'))
            status = item.get('initiativeStatus')
            short_title = item.get('shortTitle')
            info.append({'id': id, 'status': status, 'short_title': short_title})
            print(f'{id} success')
        if total_pages is None:
            total_pages = data.get('page', {}).get('totalPages', 0)
            
        if page >= total_pages:
            break
        page += 1
        
        time.sleep(time_period)
    
    
    with open(f'{output_path}/initiatives_id.json', 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=4)
        
    return info

def main():
    topic = 'AGRI'
    size = 10
    language = 'EN'
    url = url_initiatives_id
    initiatives_id = get_init_id(url, topic, size, language)
    print ('data processing completed')

if __name__ == '__main__':
    SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    url_initiatives_id = 'https://ec.europa.eu/info/law/better-regulation/brpapi/searchInitiatives?'
    main()
    