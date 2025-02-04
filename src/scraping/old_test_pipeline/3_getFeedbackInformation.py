# get all feedback infomation with publicationId
# https://ec.europa.eu/info/law/better-regulation/api/allFeedback?publicationId={?}&keywords=&language=EN&page=0&size=10&sort=dateFeedback,DESC
#-------------#
# download pdf, with documentId, https://ec.europa.eu/info/law/better-regulation/api/download/{?}

import requests
import json
import os
import time

# get publicationId, id, frontendstage from p_id json
def get_publicationId_list(file_path):
    pubid = []
    with open(file_path, 'r') as f:
        data = json.load(f)
        for i in data:
            id = i['id']
            publication_ids = [item['publicationId'] for item in i['info']]
            frontendstage = [item['frontEndStage'] for item in i['info']]
            id_dic = {'id': id, 'publicationId': publication_ids, 'frontEndStage': frontendstage}
            pubid.append(id_dic)
    print(pubid)
    return pubid

# get feedback info with publicationId
def get_feedback_info(pubid):

    if not os.path.exists(output_path):
        os.makedirs(output_path)       
    
    feedback_info = []
    base_url = "https://ec.europa.eu/info/law/better-regulation/api/allFeedback?publicationId={}&keywords=&language=EN&page={}&size=10&sort=dateFeedback,DESC"
    
    for item in pubid:
        id = item['id']
        publicationId = item['publicationId']
        frontendstage = item['frontEndStage']
        for i, pub_id in enumerate(publicationId):
            page_number = 0
            while True:
                url = base_url.format(pub_id, page_number)
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    
                    # check if there is any feedback
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
                    
                    if feedback_content is not None:
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
                    new_dic = {
                        'id': id,
                        'publicationId': pub_id,
                        'frontEndStage': frontendstage[i],
                        'feedback': 'no data'
                    }
                    feedback_info.append(new_dic)
                    break
                time.sleep(1)
                
            print(f'{id} {pub_id} {frontendstage[i]} done')
                    
    with open(final_file, 'w') as f:
        json.dump(feedback_info, f, indent=4)
        
    return feedback_info
                
if __name__ == '__main__':   
    topic = 'AGRI'
    SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    file_path = os.path.join(SRC_DIR, 'data', topic, 'p_id.json')
    output_path = os.path.join(SRC_DIR, 'data', topic)
    final_file = os.path.join(output_path, 'feedback_info.json')
    
    get_feedback_info(get_publicationId_list(file_path))
    