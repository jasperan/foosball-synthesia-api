import oci
import json
# Setup basic variables
# Auth Config
# TODO: Please update config profile name and use the compartmentId that has policies grant permissions for using Generative AI Service
compartment_id = "ocid1.compartment.oc1..aaaaaaaaz45igkuqrqzykarohxzaihsx4sroixg4atamzdqawysademdkasq"
CONFIG_PROFILE = "DEFAULT"
config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)

# Service endpoint
endpoint = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

generative_ai_inference_client = oci.generative_ai_inference.GenerativeAiInferenceClient(config=config, service_endpoint=endpoint, retry_strategy=oci.retry.NoneRetryStrategy(), timeout=(10,240))
generate_text_detail = oci.generative_ai_inference.models.GenerateTextDetails()
llm_inference_request = oci.generative_ai_inference.models.CohereLlmInferenceRequest()
llm_inference_request.prompt = "Hello, how are you?"
llm_inference_request.max_tokens = 600
llm_inference_request.temperature = 1
llm_inference_request.frequency_penalty = 0
llm_inference_request.top_p = 0.75

generate_text_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id="ocid1.generativeaimodel.oc1.us-chicago-1.amaaaaaask7dceyafhwal37hxwylnpbcncidimbwteff4xha77n5xz4m7p6a")
generate_text_detail.inference_request = llm_inference_request
generate_text_detail.compartment_id = compartment_id
generate_text_response = generative_ai_inference_client.generate_text(generate_text_detail)
# Print result
print("**************************Generate Texts Result**************************")
#print(generate_text_response.data)

data_dict = vars(generate_text_response)

json_result = json.loads(str(data_dict['data']))

print(json_result['inference_response']['generated_texts'][0]['text']), type(json_result)
    
#data_dict = vars(generate_text_response)

response_data = {
    'text': json_result['inference_response']['generated_texts'][0]['text'],
    'game_instance_id': 22,
}

print(response_data)