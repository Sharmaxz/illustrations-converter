import os
import json
import environ
import requests
from PIL import Image
from google.cloud import storage

path = os.path.dirname(os.path.realpath(__file__)) + '/media'

env = environ.Env()
environ.Env.read_env()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = env('GOOGLE_APPLICATION_CREDENTIALS')
bucket_name = env('BUCKET_NAME')
bucket_path_orig = env("BUCKET_ORIGINAL_FOLDER")
bucket_path_small = env("BUCKET_SMALL_FOLDER")

storage_client = storage.Client()
bucket = storage_client.get_bucket(bucket_name)


def remove(jpg, psd):
    os.remove(jpg)
    os.remove(psd)


def uploud_to_small(local, file_name):
    blob = bucket.blob(bucket_path_small + f'{file_name}.jpeg')
    blob.upload_from_filename(local)
    print('Uplouded!')


def converter(files):
    for file in files:
        psd_file = f'{path}/psd/{file}.psd'
        jpg_file = f'{path}/jpg/{file}.jpg'
        try:
            print("----------------------")
            blob = bucket.blob(f'{bucket_path_orig}{file}.psd')
            blob.download_to_filename(psd_file)
            print(f"Illustration {file}.psd downloaded to ../media/psd/")

            Image.MAX_IMAGE_PIXELS = None
            image = Image.open(psd_file)
            image.save(jpg_file)
            print(f"Illustration {file}.jpeg downloaded to ../media/jpg/")

            uploud_to_small(jpg_file, file)
            remove(jpg_file, psd_file)
        except:
            print(file, 'err')

        print("----------------------")


def update_deploy(file_list):
    code_result = []

    response = requests.get(url=env('HEROKU_URL'), headers={'Authorization': f"Bearer {env('AUTHORIZATION')}"})
    file_heroku = json.loads(response.content)

    for file in file_heroku:
        if file['image'] is None:
            code_result.append(file['code'])

    diff_list = list(set(code_result) - set(file_list))


def compare(bucket):
    files_original = bucket.list_blobs(prefix=bucket_path_orig)
    files_small = bucket.list_blobs(prefix=bucket_path_small)
    original_list = [os.path.splitext(os.path.basename(file.name))[0] for file in files_original if '.' in file.name]
    small_list = [os.path.splitext(os.path.basename(file.name))[0] for file in files_small if '.' in file.name]

    diff_list = list(set(original_list) - set(small_list))
    print(f'Total of difference: {len(diff_list)}')
    # update_deploy(diff_list)
    # converter(diff_list)


compare(bucket)
