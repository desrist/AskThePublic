# get documentId from feedback_info.json,  generate attachments.json
# download pdf with the url https://ec.europa.eu/info/law/better-regulation/api/download/{documentId}

import aiohttp
import asyncio
import json
import os
import aiofiles

async def fetch(session, url, file_path, semaphore):
    async with semaphore:
        if os.path.exists(file_path):
            print(f"File {file_path} already exists, skipping download.")
            return
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    async with aiofiles.open(file_path, 'wb') as f:
                        await f.write(await response.read())
                    print(f"Downloaded {file_path}")
                else:
                    print(f"Failed to download {file_path}: HTTP {response.status}")
        except Exception as e:
            print(f"Error downloading {file_path}: {e}")

async def download_attachments(attachment_list, download_dir, concurrent_limit, delay):
    semaphore = asyncio.Semaphore(concurrent_limit)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for attachment in attachment_list:
            file_name = attachment['attachment_info']['fileName']
            document_id = attachment['attachment_info']['documentId']
            url = f"https://ec.europa.eu/info/law/better-regulation/api/download/{document_id}"
            file_path = os.path.join(download_dir, file_name)

            # Ensure download directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            task = asyncio.create_task(fetch(session, url, file_path, semaphore))
            tasks.append(task)
            await asyncio.sleep(delay)  # Delay between requests
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    topic = 'AGRI'
    SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_dir = os.path.join(SRC_DIR, 'data', topic)

    # Prompt user to set download directory
    download_dir = os.path.join(SRC_DIR, 'download', topic)
    os.makedirs(download_dir, exist_ok=True)

    # Load attachment list from JSON file
    attachment_file_path = os.path.join(data_dir, 'attachments.json')
    with open(attachment_file_path, 'r') as f:
        attachment_list = json.load(f)

    # Set concurrent limit and delay between downloads
    concurrent_limit = int(input("Enter the number of concurrent downloads (default: 5): ").strip() or 5)
    delay = float(input("Enter the delay between downloads in seconds (default: 1): ").strip() or 1)

    # Start downloading
    asyncio.run(download_attachments(attachment_list, download_dir, concurrent_limit, delay))
