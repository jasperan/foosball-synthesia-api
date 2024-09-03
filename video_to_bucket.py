import oci
import requests
import os
import urllib.request

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

def upload_to_bucket(object_name):
    with open(object_name, 'rb') as f:
        try:
            object_storage.put_object(namespace, bucket_name, object_name, f)
        except oci.exceptions.ServiceError as e:
            print(f"OCI Service Error occurred: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error occurred while uploading object: {e}")
            raise

def main(video_url, game_instance_id):
    try:
        file_name = download_video(video_url, game_instance_id)
        upload_to_bucket(file_name)
        print(f"Video uploaded successfully as {game_instance_id}.mp4")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    #finally:
    #    if os.path.exists(object_name):
    #        os.remove(object_name)

if __name__ == "__main__":
    video_url = "https://synthesia-ttv-data.s3.amazonaws.com/video_data/f36aa70e-c643-4ec4-9216-5b54966782c1/transfers/rendered_video.mp4?response-content-disposition=attachment%3Bfilename%3D%22Game%20Instance%20ID%20%2322.mp4%22&AWSAccessKeyId=AKIA32NGJ5TSQOTYGMPR&Signature=ndWwAT57iP7C%2B1sUN9K0qNoW9RU%3D&Expires=1725425000"  # Replace with actual URL
    main(video_url, "1")