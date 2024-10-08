import oci
import yaml
from flask import Flask, request, jsonify
import requests
import json 


app = Flask(__name__)

with open('config.yaml', 'r') as file:
    config_data = yaml.safe_load(file)

compartment_id = config_data['compartment_id']
CONFIG_PROFILE = config_data['config_profile']
config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)

# Service endpoint
endpoint = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"



@app.route('/generate', methods=['GET'])
def generate():

    # Get parameters from the GET request
    data = request.args.to_dict()

    print(data)

    game_instance_id = data['game_instance_id']
    del data['game_instance_id']

    request_type = data['request_type']

    '''
    - Goals per team: {}
        - Ball possession percentage: {}
        - Possession total (in seconds): {}
        - Match duration (in seconds): {}
        - Number of players: {}
    '''

    if request_type == 'match':

        construct_query = """
        You are a professional football commentator. You have been invited to host a foosball tournament with matches of 3 minutes in length. There are two teams. I need you to give me your best narration as if it were a live football match. Use the past tense.
        
        Team 1, Hornets (Yellow shirts [appears as "red" in the database]) vs Team 2: Panthers (Black shirts [appears as "blue" in the database])
        
        Here are some statistics about the match these two teams just played. Use this information as basis for your narration, and be specific about the numbers:


        - Goals per team: {}
        - Possession percentage: {}
        - Match duration: {} seconds
        - Number of players: {}

        In your result, reduce the risk of sounding like a war, i.e. prevent the use of words like battle, war, attack, fight, destroyed, killed, sniper, bullet, weapon, etc.
        
        After talking about the stats, stop generating more text.
        """.format(data['goals_per_team'],
                data['possession_percentage'],
                #data['possession_total'],
                data['match_duration'],
                data['number_of_players'])
    #   Do NOT end your response with further questions to the user and do not finish your generations mid-sentence.


    elif request_type == 'progressive':
        
        construct_query = """
        You are a professional football commentator. You have been invited to host a foosball tournament with round-robin matches of 3 minutes in length, and you have been the main commentator of these games. There are two teams.
         
        I need you to give me a report of the games that have already been played - you don't need to commentate a new game, but rather make a post-match analysis of what happened and how you think the matches have been so far in the tournament.

        Use the past tense. Use 150 words or less.
        
        Team 1, Hornets (Yellow shirts [appears as "red" in the database]) vs Team 2: Panthers (Black shirts [appears as "blue" in the database])

        Here are some statistics about the match these two teams just played. Use this information as basis for your narration, and be specific about the numbers when mentioning statistics:

        - Goals per team: {}
        - Possession percentage: {}
        - Possession total: {} seconds
        - Match duration: {} seconds
        - Number of players: {}

        In your result, reduce the risk of sounding like a war, i.e. prevent the use of words like battle, war, attack, fight, destroyed, killed, sniper, bullet, weapon, etc.
        
        After talking about the stats, stop generating more text.
        """.format(data['goals_per_team'],
                data['possession_percentage'],
                data['possession_total'],
                data['match_duration'],
                data['number_of_players_and_games_played'])
        
        

    else:
        print('Invalid request type! Valid values are [match, progressive]')
        return -1


    print(construct_query)

    max_tokens = 450 if request_type == 'match' else 550


    generative_ai_inference_client = oci.generative_ai_inference.GenerativeAiInferenceClient(config=config, service_endpoint=endpoint, retry_strategy=oci.retry.NoneRetryStrategy(), timeout=(10,240))
    chat_detail = oci.generative_ai_inference.models.ChatDetails()

    content = oci.generative_ai_inference.models.TextContent()
    content.text = construct_query
    message = oci.generative_ai_inference.models.Message()
    message.role = "USER"
    message.content = [content]

    llm_inference_request = oci.generative_ai_inference.models.GenericChatRequest()
    llm_inference_request.api_format = oci.generative_ai_inference.models.BaseChatRequest.API_FORMAT_GENERIC
    llm_inference_request.messages = [message]

    llm_inference_request.max_tokens = int(data.get('max_tokens', max_tokens))
    llm_inference_request.temperature = float(data.get('temperature', 1))
    llm_inference_request.frequency_penalty = float(data.get('frequency_penalty', 0))
    llm_inference_request.top_p = float(data.get('top_p', 0.75))

    chat_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id="ocid1.generativeaimodel.oc1.us-chicago-1.amaaaaaask7dceyaycmwwnvu2gaqrffquofgmshlqzcdwpk727n4cykg34oa")
    chat_detail.chat_request = llm_inference_request
    chat_detail.compartment_id = compartment_id
    chat_response  = generative_ai_inference_client.chat(chat_detail)

    '''
    llm_inference_request.prompt = construct_query
    llm_inference_request.max_tokens = int(data.get('max_tokens', max_tokens))
    llm_inference_request.temperature = float(data.get('temperature', 1))
    llm_inference_request.frequency_penalty = float(data.get('frequency_penalty', 0))
    llm_inference_request.top_p = float(data.get('top_p', 0.75))
    llm_inference_request.top_k = int(data.get('top_k', 0))

    generate_text_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id="ocid1.generativeaimodel.oc1.us-chicago-1.amaaaaaask7dceyaycmwwnvu2gaqrffquofgmshlqzcdwpk727n4cykg34oa")
    generate_text_detail.inference_request = llm_inference_request
    generate_text_detail.compartment_id = compartment_id
    generate_text_response = generative_ai_inference_client.generate_text(generate_text_detail)
    '''
    print("**************************Generate Texts Result**************************")
    
    data_dict = vars(chat_response)
    print(data_dict)

    json_result = json.loads(str(data_dict['data']))
    print(json_result['chat_response']['choices'][0]['message']['content'][0]['text']), type(json_result)

        #data_dict = vars(generate_text_response)

    response_data = {
        'text': json_result['chat_response']['choices'][0]['message']['content'][0]['text'],
        'game_instance_id': game_instance_id,
    }


    # Post response_data to localhost:3500/synthesia
    try:
        synthesia_response = requests.post('http://localhost:3501/synthesia', json=response_data)
        synthesia_response.raise_for_status()  # Raise an exception for bad status codes
        print("Data sent successfully to Synthesia endpoint. Response:", synthesia_response.text)
    except requests.RequestException as e:
        print("Error sending data to Synthesia endpoint:", e)

    return jsonify(response_data)


if __name__ == '__main__':
    app.run(port=3500)

# cohere.command-r-plus: ocid1.generativeaimodel.oc1.us-chicago-1.amaaaaaask7dceya7ozidbukxwtun4ocm4ngco2jukoaht5mygpgr6gq2lgq
# cohere.command for generation: ocid1.generativeaimodel.oc1.us-chicago-1.amaaaaaask7dceyafhwal37hxwylnpbcncidimbwteff4xha77n5xz4m7p6a


# new model - llama3: ocid1.generativeaimodel.oc1.us-chicago-1.amaaaaaask7dceyaycmwwnvu2gaqrffquofgmshlqzcdwpk727n4cykg34oa