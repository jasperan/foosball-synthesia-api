import requests
import yaml
from verify_download import verify_download

# endpoint URL
url = "https://api.synthesia.io/v2/videos"


# data payload
payload = {
    "test": True,
    "visibility": "private",
    "aspectRatio": "16:9",
    "title": "Default video title",
    "description": "Default video description",
    "soundtrack": "inspirational",
    "input": [
        {
            "avatarSettings": {
                "horizontalAlign": "center",
                "scale": 1,
                "style": "rectangular",
                "seamless": False
            },
            "backgroundSettings": { "videoSettings": {
                    "shortBackgroundContentMatchMode": "freeze",
                    "longBackgroundContentMatchMode": "trim"
                } },
            "avatar": "anna_costume1_cameraA",
            "scriptText": "What is up ladies and gentleman from Oracle? This is a generation example using the test version of the API",
            "background": "green_screen"
        }
    ]
}

# Set up the headers
headers = {
    "Authorization": yaml.safe_load(open('config.yaml'))['authorization'],
    "accept": "application/json",
    "content-type": "application/json"
}


# Send the POST request
response = requests.post(url, json=payload, headers=headers)

# Print the response
print(response.status_code)
print(response.json())

# from response, retrieve video id, which will be the same after processing

if response.status_code == 201:
    status = response.json()['status']
    video_id = response.json()['id']

else:
    status = None
    video_id = None

print('{} - {}'.format(
    video_id,
    status
))

if not video_id is None:
    download_url = verify_download(video_id)