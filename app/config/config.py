import json
import os
from pydantic import BaseModel, ValidationError
from typing import List

class Config(BaseModel):
    log_level: str
    cloudflare_zone_id: List[str]
    cloudflare_api_token: List[str]
    test_interval: int
    rabbitmq_url: str
    rabbitmq_exchangeout: str
    rabbitmq_exchangedefault: str
    imap_server: str
    imap_port: int
    imap_user: str
    imap_password: str


try:
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    config_sample = os.path.join(os.path.dirname(__file__), 'config_sample.json')
    config_data = {}
    if os.path.exists(config_sample):
        with open(config_sample) as f:
            sample_data = json.load(f)
        for key, value in sample_data.items():
            config_data[key] = value
    env_vars = {
        "log_level": os.environ.get('log_level') or "INFO",
        "cloudflare_zone_id": ((os.environ.get('cloudflare_zone_id')).split(", ") if os.environ.get('cloudflare_zone_id') else []),
        "cloudflare_api_token": ((os.environ.get('cloudflare_api_token')).split(", ") if os.environ.get('cloudflare_api_token') else []),
        "test_interval": int(os.environ.get('test_interval')) if os.environ.get('test_interval') else 10,
        "rabbitmq_url": os.environ.get('rabbitmq_url') if os.environ.get('rabbitmq_url') else "amqp://guest:guest@localhost:5672/",
        "rabbitmq_exchangeout": os.environ.get('rabbitmq_exchangeout') if os.environ.get('rabbitmq_exchangeout') else "output",
        "rabbitmq_exchangedefault": os.environ.get('rabbitmq_exchangedefault') if os.environ.get('rabbitmq_exchangedefault') else "default",
        "imap_server": os.environ.get('imap_server') if os.environ.get('imap_server') else "imap.gmail.com",
        "imap_port": int(os.environ.get('imap_port')) if os.environ.get('imap_port') else 993,
        "imap_user": os.environ.get('imap_user') if os.environ.get('imap_user') else "",
        "imap_password": os.environ.get('imap_password') if os.environ.get('imap_password') else ""
    }
    for key, value in env_vars.items():
        if value is not None:
            config_data[key] = value
    if os.path.exists(config_path):
        with open(config_path) as f:
            config_data = json.load(f)
    config = Config(**config_data)
    if len(config.cloudflare_zone_id) != len(config.cloudflare_api_token):
        raise ValidationError
except (json.JSONDecodeError, FileNotFoundError) as e:
    print(f"Error reading config file: {e}")
    raise
