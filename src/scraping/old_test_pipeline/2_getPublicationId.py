"""
type: INIT_PLANNED // IMPACT_ASSESS_INCEP: Impact Assessment Inception // OPC launched: Open Public Consultation // PROP_REG: Proposal Regulation,
      Roadmap // SWD: staff working document // REG_IMPL_DRAFT: Regulation Implementation Draft//REG_IMPL // REG_DEL_DRAFT: Regulation Delegated Draft // REG_DEL

stage: PLANNING_WORKFLOW // ISC_WORKFLOW: Inter-Service Consultation Workflow // ADOPTION_WORKFLOW
"""
# get p-id

import requests
import os
import time
import json

def get_init_id(file_path):
    id_list = []
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            id_list.append(item['id'])
        
    return id_list

def get_publicationId(id_list):
    info_big = []
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        
    for id in id_list:
        url = 'https://ec.europa.eu/info/law/better-regulation/brpapi/groupInitiatives/' + f'{id}'
        response = requests.get(url)
        if response.status_code != 200:
            print('Error:', response.status_code)
            break
        data = response.json()
        publications_data = data.get('publications', [])
        # print(publications)
        info_small = []
        for item in publications_data:
            publi_id = item.get('id')
            type = item.get('type')
            stage = item.get('stage')
            total_Feedback = item.get('totalFeedback')
            groupId = item.get('groupId')
            frontEndStage = item.get('frontEndStage')
            createdDate = item.get('createdDate')
            publishedDate = item.get('publishedDate')
            endDate = item.get('endDate')
            info_small.append({'publicationId': publi_id, 'type': type, 'stage': stage, 'total_Feedback': total_Feedback, 'groupId': groupId, 'frontEndStage': frontEndStage, 'createdDate': createdDate, 'publishedDate': publishedDate, 'endDate': endDate})
        
        info_big.append({'id': id, 'info': info_small})
        print(f'{id} done')
        
    with open(final_file, 'w', encoding='utf-8') as f:
        json.dump(info_big, f, ensure_ascii=False, indent=4)
        print('Successfully processed')
        # print(info_big)
    return info_big
    
if __name__ == '__main__':
    topic = 'AGRI'
    SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    file_path = os.path.join(SRC_DIR, 'data', topic, 'initiatives_id.json')
    output_path = os.path.join(SRC_DIR, 'data', topic)
    final_file = os.path.join(output_path, 'p_id.json')
    
    id_list = get_init_id(file_path)
    get_publicationId(id_list)
    print('All done')