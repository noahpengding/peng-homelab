import os
from pydantic import BaseModel, ValidationError
from typing import List


class Config(BaseModel):
    log_level: str
    app_name: str = "Peng-Homelab"
    host: str
    port: int
    admin_password: str
    jwt_secret_key: str
    # IMAP configuration
    imap_server: str
    imap_port: int = 993
    imap_user: str
    imap_password: str
    # Vaultwarden configuration
    vaultwarden_client_id: str
    vaultwarden_client_secret: str
    vaultwarden_host: str
    vaultwarden_email: str
    vaultwarden_password: str
    vaultwarden_org_id: str
    # Email scheduling configuration
    schedule_check_email_address: str
    schedule_check_email_password: str
    smtp_server: str
    smtp_port: int = 465
    smtp_use_ssl: bool = True
    s3_url: str
    s3_access_key: str
    s3_secret_key: str
    s3_bucket: str
    s3_base_path: str
    email_path: str


try:
    config_data = {}
    env_vars = {
        "log_level": os.environ.get("log_level") or "INFO",
        "app_name": os.environ.get("app_name") or "Peng-Homelab",
        "host": os.environ.get("host") if os.environ.get("host") else "0.0.0.0",
        "port": int(os.environ.get("port")) if os.environ.get("port") else 8000,
        "admin_password": os.environ.get("admin_password") if os.environ.get("admin_password") else "admin123",
        "jwt_secret_key": os.environ.get("jwt_secret_key") if os.environ.get("jwt_secret_key") else "your_secret_key",
        "imap_server": os.environ.get("imap_server")
        if os.environ.get("imap_server")
        else "imap.gmail.com",
        "imap_port": int(os.environ.get("imap_port"))
        if os.environ.get("imap_port")
        else 993,
        "imap_user": os.environ.get("imap_user") if os.environ.get("imap_user") else "",
        "imap_password": os.environ.get("imap_password")
        if os.environ.get("imap_password")
        else "",
        # Vaultwarden configuration
        "vaultwarden_client_id": os.environ.get("vaultwarden_client_id")
        if os.environ.get("vaultwarden_client_id")
        else "user.521d1f79-d55f-4f7e-86c8-cfb17ded7fd9",
        "vaultwarden_client_secret": os.environ.get("vaultwarden_client_secret")
        if os.environ.get("vaultwarden_client_secret")
        else "dFd14BmpmaInbZlXkmtfgiPEqAtH77",
        "vaultwarden_host": os.environ.get("vaultwarden_host")
        if os.environ.get("vaultwarden_host")
        else "https://vaultwarden.example.com",
        "vaultwarden_email": os.environ.get("vaultwarden_email")
        if os.environ.get("vaultwarden_email")
        else "",
        "vaultwarden_password": os.environ.get("vaultwarden_password")
        if os.environ.get("vaultwarden_password")
        else "",
        "vaultwarden_org_id": os.environ.get("vaultwarden_org_id")
        if os.environ.get("vaultwarden_org_id")
        else "1b6422d7-2c9d-4085-bbd1-6ff585b41e28",
        # Email scheduling configuration
        "schedule_check_email_address": os.environ.get("schedule_check_email_address")
        if os.environ.get("schedule_check_email_address")
        else "",
        "schedule_check_email_password": os.environ.get("schedule_check_email_password")
        if os.environ.get("schedule_check_email_password")
        else "",
        "smtp_server": os.environ.get("smtp_server")
        if os.environ.get("smtp_server")
        else "smtp.gmail.com",
        "smtp_port": int(os.environ.get("smtp_port"))
        if os.environ.get("smtp_port")
        else 465,
        "smtp_use_ssl": bool(os.environ.get("smtp_use_ssl"))
        if os.environ.get("smtp_use_ssl") is not None
        else True,
        "s3_url": os.environ.get("s3_url")
        if os.environ.get("s3_url")
        else "https://minio.example.com",
        "s3_access_key": os.environ.get("s3_access_key")
        if os.environ.get("s3_access_key")
        else "",
        "s3_secret_key": os.environ.get("s3_secret_key")
        if os.environ.get("s3_secret_key")
        else "",
        "s3_bucket": os.environ.get("s3_bucket") if os.environ.get("s3_bucket") else "",
        "s3_base_path": os.environ.get("s3_base_path") if os.environ.get("s3_base_path") else "homelab",
        "email_path": os.environ.get("email_path")
        if os.environ.get("email_path")
        else "/tmp",
    }
    for key, value in env_vars.items():
        if value is not None:
            config_data[key] = value
    config = Config(**config_data)
except ValidationError as e:
    print("Configuration error:", e)
    raise
