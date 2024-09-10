import requests
import yaml
from verify_download import verify_download


avatars = {
    'brendan': 'f05b2c94-6c0c-4d71-82e5-90fd51c7eea3',
    'brendan_v2': '209701e1-77a3-40d2-a383-1bd115f0ab0e',
    'brendan_v3': 'b449c042-ab6c-421c-b09a-baeab47d5960',
}

url = "https://api.synthesia.io/v2/videos"

# Set up the headers
headers = {
    "Authorization": yaml.safe_load(open('config.yaml'))['authorization'],
    "accept": "application/json",
    "content-type": "application/json"
}



game_instance_id = 22


# Define the data payload
payload = {
    "test": False,
    "visibility": "private",
    "aspectRatio": "16:9",
    "title": "Game Instance ID #{}".format(game_instance_id),
    "description": "Video for game instance ID #{}".format(game_instance_id),
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
            "avatar": avatars['brendan_v3'], # anna_costume1_cameraA
            "scriptText": 'Hello this is a Synthesia test',  # update script text
            "background": "green_screen"
        }
    ]
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

if video_id:
    download_url = verify_download(video_id)
else:
    download_url = 'Invalid URL'


print(download_url)