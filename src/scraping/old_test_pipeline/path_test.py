import os
from dotenv import load_dotenv

# get root path
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
file_path = os.path.join(SRC_DIR, 'data', 'AGRI', 'initiatives_id.json')
print(file_path)