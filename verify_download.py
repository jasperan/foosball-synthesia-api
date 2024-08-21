import requests
import time
import yaml

def verify_download(video_id):
    url = f"https://api.synthesia.io/v2/videos/{video_id}"
    headers = {
        "Authorization": yaml.safe_load(open('config.yaml'))['authorization'],
        "accept": "application/json"
    }

    while True:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            
            if status == 'complete':
                download_url = data.get('download')
                if download_url:
                    print(f"Video is ready. Download URL: {download_url}")
                    return download_url
                else:
                    print("Video is complete, but download URL is not available.")
                    return None
            elif status == 'failed':
                print("Video generation failed.")
                return None
            else:
                print(f"Video status: {status}. Waiting...")
                time.sleep(10)  # Wait for 30 seconds before checking again
        else:
            print(f"Error checking video status. Status code: {response.status_code}")
            return None

# Usage example:
# download_url = verify_download(video_id)
download_url = verify_download("cbda58b3-6ad2-4878-8bde-dbe61ac2d257")