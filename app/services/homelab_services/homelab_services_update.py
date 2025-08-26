from app.utils.minio_connection import MinioStorage
from app.config.config import config
from app.utils.log import output_log
import pandas as pd


def update_homelab_services(service_name: str, old_image_id: str, new_image_id: str):
    minio = MinioStorage()
    minio.file_download(f"{config.s3_base_path}/Services_all.xlsx", "Services_all.xlsx")

    try:
        df = pd.read_excel("Services_all.xlsx")
        df.loc[
            (df["Service"] == service_name) & (df["Image ID"] == old_image_id),
            "Image ID",
        ] = new_image_id
        df.to_excel("Services_all.xlsx", index=False)
    except Exception as e:
        output_log(f"Error updating services Excel file: {e}", "error")
        return False
    minio.file_upload(
        "Services_all.xlsx",
        f"{config.s3_base_path}/Services_all.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    return True
