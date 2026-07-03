import os
from google.cloud import storage

client = storage.Client()

def download_if_missing(bucket_name, blob_path, local_path):
    if os.path.exists(local_path):
        return local_path

    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.download_to_filename(local_path)

    return local_path
