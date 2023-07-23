import os
import boto3
from dotenv import load_dotenv
from pathlib import Path
from vortex_ingester import PERSIST_DIRECTORY
from mypy_boto3_s3.service_resource import Bucket
from vortex_ingester import VortexIngester

load_dotenv()


def main():
    ingester = VortexIngester("./docs/")
    ingester.ingest()

    client = boto3.resource("s3")
    bucket = client.Bucket("gladstone-gpt-data")
    delete_folder(bucket)
    upload_folder(Path(PERSIST_DIRECTORY), bucket)


def delete_folder(bucket: Bucket):
    for object in bucket.objects.all():
        object.delete()


def upload_folder(folder: Path, bucket: Bucket):
    # enumerate local files recursively
    for subdir, dirs, files in os.walk(folder):
        for file in files:
            full_path = os.path.join(subdir, file)
            with open(full_path, "rb") as data:
                bucket.put_object(Key=full_path[len(str(folder)) + 1 :], Body=data)


def upload_file(file_name: Path, bucket: Bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    with open(file_name, "rb") as data:
        bucket.put_object(Key=str(file_name), Body=data)


if __name__ == "__main__":
    main()
