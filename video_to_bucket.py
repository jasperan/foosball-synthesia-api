import oci
import requests
import os
import urllib.request
import pytz 
from oci.object_storage.models import CreatePreauthenticatedRequestDetails
from datetime import datetime, timedelta

# OCI configuration
CONFIG_PROFILE = "DEFAULT"
config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)
object_storage = oci.object_storage.ObjectStorageClient(config)

# Bucket details
namespace = object_storage.get_namespace().data

print('Bucket namespace: {}'.format(namespace))

bucket_name = "bucket-20240903-1708"

def download_video(url, game_instance_id):
    #urllib.request.urlretrieve(url, object_name) 
    
    response = requests.get(url)
    response.raise_for_status()

    file_name = "{}.mp4".format(game_instance_id)
    try:
        with open(file_name, 'wb') as f:
            f.write(response.content)
    except IOError as e:
        print(f"Error writing file: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        raise
    
    return file_name

def upload_to_bucket(object_name, bucket_name, object_storage, namespace):
    with open(object_name, 'rb') as f:
        try:
            object_storage.put_object(namespace, bucket_name, object_name, f)
        except oci.exceptions.ServiceError as e:
            print(f"OCI Service Error occurred: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error occurred while uploading object: {e}")
            raise

def create_par(object_name, bucket_name, object_storage, namespace):
    # Creating a Pre-Authenticated Request
    par_ttl = (datetime.utcnow() + timedelta(hours=24*30)).replace(tzinfo=pytz.UTC)

    create_par_details = CreatePreauthenticatedRequestDetails()
    create_par_details.name = "PAR_{}".format(object_name)
    create_par_details.object_name = object_name
    create_par_details.access_type = CreatePreauthenticatedRequestDetails.ACCESS_TYPE_OBJECT_READ
    create_par_details.time_expires = par_ttl.isoformat()

    par = object_storage.create_preauthenticated_request(namespace_name=namespace, bucket_name=bucket_name,
                                                        create_preauthenticated_request_details=create_par_details)

    # Get Object using the Pre-Authenticated Request
    par_request_url = object_storage.base_client.get_endpoint() + par.data.access_uri

    print(par_request_url)

    return par_request_url

def main(video_url, game_instance_id):
    try:
        file_name = download_video(video_url, game_instance_id)
        upload_to_bucket(file_name, bucket_name, object_storage, namespace)
        par_url = create_par(file_name, bucket_name, object_storage)
        print(f"Video uploaded successfully as {game_instance_id}.mp4")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    #finally:
    #    if os.path.exists(object_name):
    #        os.remove(object_name)

if __name__ == "__main__":
    video_url = "https://synthesia-ttv-data.s3.amazonaws.com/video_data/f8265796-3a5d-4d5e-a087-bbe3f9db5651/transfers/rendered_video.mp4?response-content-disposition=attachment%3Bfilename%3D%22Game%20Instance%20ID%20%23313.mp4%22&AWSAccessKeyId=AKIA32NGJ5TSQOTYGMPR&Signature=jMhgA7K%2B14cmSHE%2BU%2FPG5E77Ns0%3D&Expires=1725559062"  # Replace with actual URL
    main(video_url, "111")