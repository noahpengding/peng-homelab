from minio import Minio
from app.config.config import config
from app.utils.log import output_log


class MinioStorage:
    def __init__(self):
        self.entrypoint = config.minio_entrypoint
        self.access_key = config.minio_access_key
        self.secret_key = config.minio_secret_key
        self.client = Minio(
            self.entrypoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=True,
        )

    def file_upload(self, bucket_name, file_path, file_name, content_type):
        try:
            file_name = file_name.replace("\\", "/")
            self.client.fput_object(
                bucket_name, file_name, file_path, content_type=content_type
            )
        except Exception as e:
            output_log(e, "error")
            return False
        return True

    def file_download(self, bucket_name, file_name, download_path):
        try:
            file_name = file_name.replace("\\", "/")
            self.client.fget_object(bucket_name, file_name, download_path)
        except Exception as e:
            output_log(e, "error")
            return False
        return True

    def file_list_name(self, bucket_name, prefix=None):
        try:
            objects = self.client.list_objects(
                bucket_name, prefix=prefix, recursive=True
            )
            return [obj.object_name.split(prefix + "/")[1] for obj in objects]
        except Exception as e:
            output_log(e, "error")
            return None

    def file_exists(self, bucket_name, file_name):
        try:
            file_name = file_name.replace("\\", "/")
            return self.client.stat_object(bucket_name, file_name)
        except Exception as e:
            output_log(f"{bucket_name}||{file_name}:\n{e}", "error")
            return False

    def remove_file(self, bucket_name, file_name):
        try:
            self.client.remove_object(bucket_name, file_name)
        except Exception as e:
            output_log(e, "error")
            return False
        return True
