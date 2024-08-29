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
                "scriptText": data['game_instance_id'],
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
        except Exception as e:
            print("No download URL available to send: {}".format(e))


        return jsonify({"message": "Script text updated successfully"}), 200
    else:
        return jsonify({"error": "Invalid data received"}), 400
            







#verify_download(video_id) - u can use this for testing if the download was OK.


if __name__ == '__main__':
    app.run(port=3501)
