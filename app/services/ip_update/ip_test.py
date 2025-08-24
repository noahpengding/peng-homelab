from app.utils.minio_connection import MinioStorage
from app.utils.log import output_log
from app.config.config import config
import pandas as pd
import os

def _get_zone_result() -> dict:
    minio = MinioStorage()
    try:
        minio.file_download(f"{config.s3_base_path}/cloudflare_dns.xlsx", "zone_id.xlsx")
        df = pd.read_excel("zone_id.xlsx").to_dict(orient="records")
        os.remove("zone_id.xlsx")
        return df
    except Exception as e:
        output_log(f"Error getting zone info from Minio: {e}", "error")
        return {}

def get_dns_result(record_name):
    zone_info = _get_zone_result()
    for zone in zone_info:
        if record_name.endswith(zone["Zone"]):
            from app.services.ip_update.cloudflare import Cloudflare
            cf = Cloudflare(zone["Zone_id"], zone["Token"])
            record = cf.get_dns_record(record_name)
            return record
        
def update_dns(current_ip, new_ip):
    zone_info = _get_zone_result()
    for zone in zone_info:
        from app.services.ip_update.cloudflare import Cloudflare
        cf = Cloudflare(zone["Zone_id"], zone["Token"])
        cf.update_dns(current_ip, new_ip)
