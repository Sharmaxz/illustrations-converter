from os import path
from google.cloud import storage
import environ

BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))
env = environ.Env()
environ.Env.read_env()

client = storage.Client.from_service_account_json(f"{BASE_DIR}/illustrations-converter/{env('GOOGLE_APPLICATION_CREDENTIALS')}")
bucket_name = env('BUCKET_NAME')
bucket = client.get_bucket(bucket_name)


def list_files(bucket):
    files = bucket.list_blobs(prefix=env('BUCKET_FOLDER_ORIGINAL'))
    file_list = [file.name.replace(env('BUCKET_FOLDER_ORIGINAL'), '') for file in files if '.' in file.name]
    print(file_list)


list_files(bucket)