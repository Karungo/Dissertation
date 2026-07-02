from google.cloud import storage
import os

client = storage.Client()


def download_blob(
    bucket_name,
    source_blob,
    destination_file
):

    bucket = client.bucket(
        bucket_name
    )

    blob = bucket.blob(
        source_blob
    )

    blob.download_to_filename(
        destination_file
    )

    return destination_file
