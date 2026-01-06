import boto3
from botocore.exceptions import ClientError
from app.config.config import config
from app.utils.log import output_log
import os


class S3Storage:
    def __init__(self):
        self.endpoint_url = config.s3_url
        self.access_key = config.s3_access_key
        self.secret_key = config.s3_secret_key
        output_log(
            f"S3 connection initialized to {self.endpoint_url}",
            "debug",
        )
        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )

    def file_upload(
        self, file_path, file_name, content_type, bucket_name=config.s3_bucket
    ):
        try:
            file_name = file_name.replace("\\", "/")
            self.client.upload_file(
                file_path,
                bucket_name,
                file_name,
                ExtraArgs={"ContentType": content_type},
            )
            os.remove(file_path)
        except Exception as e:
            output_log(f"Error uploading file to S3: {e}", "error")
            return False
        return True

    def file_download(self, file_name, download_path, bucket_name=config.s3_bucket):
        try:
            file_name = file_name.replace("\\", "/")
            self.client.download_file(bucket_name, file_name, download_path)
        except Exception as e:
            output_log(f"Error downloading file from S3: {e}", "error")
            return False
        return True

    def file_list_name(self, prefix="", bucket_name=config.s3_bucket):
        try:
            paginator = self.client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
            keys = []
            for page in pages:
                if "Contents" in page:
                    keys.extend([obj["Key"] for obj in page["Contents"]])
            return keys
        except Exception as e:
            output_log(f"Error listing files from S3: {e}", "error")
            return None

    def file_exists(self, file_name, bucket_name=config.s3_bucket):
        try:
            file_name = file_name.replace("\\", "/")
            self.client.head_object(Bucket=bucket_name, Key=file_name)
            return True
        except ClientError as e:
            output_log(f"ClientError checking file from S3: {e}", "error")
            return False
        except Exception as e:
            output_log(f"Error checking file from S3: {e}", "error")
            return False

    def remove_file(self, file_name, bucket_name=config.s3_bucket):
        try:
            self.client.delete_object(Bucket=bucket_name, Key=file_name)
        except Exception as e:
            output_log(f"Error removing file from S3: {e}", "error")
            return False
        return True
