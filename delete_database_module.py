# delete all the files (images on disc and cloud)
from google.cloud import storage
import parameters
import shutil

res = input(
    'you are going to delete ' + parameters.untagged_photos_dir + ' directory on your computer and in the ' + parameters.data_bucket + ' vertex AI bucket. are you sure? (type y/n) ')
if res != 'y':
    exit()


def delete(bucket=parameters.data_bucket, directory=parameters.untagged_photos_dir):
    client = storage.Client()
    bucket = client.get_bucket(bucket)
    blobs = bucket.list_blobs(prefix=directory[2:])
    for blob in blobs:
        blob.delete()
    shutil.rmtree(directory)


if res == 'y':
    delete()
