import requests
import yaml
from verify_download import verify_download

url = "https://api.synthesia.io/v2/videos"


avatars = {
    'brendan': 'f05b2c94-6c0c-4d71-82e5-90fd51c7eea3'
}


# Define the endpoint URL

# Define the data payload
'''
payload = {
    "test": False,
    "visibility": "private",
    "aspectRatio": "16:9",
    "scripttext": "What is up ladies and gentleman from Oracle? This is a generation example using the test version of the API",
    "background": "green_screen",
    "title": "My first synthetic video"
}

'''

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
            "avatar": avatars['brendan'], # anna_costume1_cameraA
            "scriptText": "What is up ladies and gentleman from Oracle? This is a generation example using the test version of the API. Civility vicinity graceful is it at.",
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




'''
# Define the data payload
# background, avatar also available.
data = {
    "test": True,
    "visibility": "private",
    "aspectRatio": "16:9",
    "avatar": "anna_costume1_cameraA",
    "background": "green_screen",
    "title": "My first synthetic video",
    "scriptText": "What is up ladies and gentlemen from Oracle? This is a generation example using the test version of the API",
    #"input": [
    #    {
    #        "avatarSettings": {
    #            "horizontalAlign": "center",
    #            "scale": 1,
    #            "style": "rectangular",
    #            "seamless": False
    #        }
    #    }
    #]
}
'''

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
    verify_download(video_id)