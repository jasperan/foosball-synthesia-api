import requests
import yaml
from verify_download import verify_download
from flask import Flask, request, jsonify

app = Flask(__name__)

# Synthesia localhost endpoint listening to POST requests.
@app.route('/synthesia', methods=['POST'])
def handle_synthesia_request():

    avatars = {
        'brendan': 'f05b2c94-6c0c-4d71-82e5-90fd51c7eea3',
        'brendan_v2': '209701e1-77a3-40d2-a383-1bd115f0ab0e',
        'brendan_v3': 'b449c042-ab6c-421c-b09a-baeab47d5960',
    }

    url = "https://api.synthesia.io/v2/videos"

    # Define the data payload
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
                "avatar": avatars['brendan_v3'], # anna_costume1_cameraA
                "scriptText": "What is up ladies and gentleman from Oracle? This is a generation example using the test version of the API. Civility vicinity graceful is it at. Improve up at to on mention perhaps raising. Way building not get formerly her peculiar. Up uncommonly prosperous sentiments simplicity acceptance to so. Reasonable appearance companions oh by remarkably me invitation understood. Pursuit elderly ask perhaps all. Wise busy past both park when an ye no. Nay likely her length sooner thrown sex lively income. The expense windows adapted sir. Wrong widen drawn ample eat off doors money. Offending belonging promotion provision an be oh consulted ourselves it. Blessing welcomed ladyship she met humoured sir breeding her. Six curiosity day assurance bed necessary. ",
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



    data = request.json
    if data and 'text' in data:
        payload['input'][0]['scriptText'] = data['text'] # update script text
        game_instance_id = data['game_instance_id']    
    
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

        # Prepare the data for the POST request
        payload = {
            "gameInstanceId": game_instance_id,
            "videoUrl": download_url
        }

        # Make the POST request
        try:
            response = requests.post(
                "https://pqyhsfxkaun3blanrjmz5tqtri.apigateway.us-ashburn-1.oci.customer-oci.com/addons/v1/gamevidurl",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()  # Raise an exception for bad status codes
            print("Video URL sent successfully. Response:", response.text)
        except requests.RequestException as e:
            print("Error sending video URL:", e)
        else:
            print("No download URL available to send.")




        return jsonify({"message": "Script text updated successfully"}), 200
    else:
        return jsonify({"error": "Invalid data received"}), 400
            







#verify_download(video_id) - u can use this for testing if the download was OK.


if __name__ == '__main__':
    app.run(port=3501)
