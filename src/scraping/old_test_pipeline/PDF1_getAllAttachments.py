# get documentId from feedback_info.json,  generate attachments.json
# download pdf with the url https://ec.europa.eu/info/law/better-regulation/api/download/{documentId}

import json
import os

# get documentId from feedback_info.json
def get_attachment_list(file_path):
    attachment_list = []
    with open(file_path, 'r') as f:
        data = json.load(f)
        for i in data:
            if i['feedback'] == 'no data':
                continue
            for feedback in i["feedback"]["_embedded"]["feedback"]:
                if 'attachments' in feedback:
                    for attachment in feedback['attachments']:
                        attachment_info = {
                            'fileName': attachment.get('ersFileName'),
                            'documentId': attachment.get('documentId')
                        }
                        attachment_list.append({
                            'id': i['id'],
                            'pid': i.get('publicationId'),
                            'attachment_info': attachment_info
                        })
    return attachment_list


if __name__ == '__main__':
    topic = 'AGRI'
    SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_dir = os.path.join(SRC_DIR, 'data', topic)
    
    # load data
    file_path = os.path.join(data_dir, 'feedback_info.json')
    attachment_list = get_attachment_list(file_path)
    
    output_path = os.path.join(data_dir, 'attachments.json')
    with open(output_path, 'w') as f:
        json.dump(attachment_list, f, indent=4)