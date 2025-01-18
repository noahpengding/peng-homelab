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
    s3_url: str
    s3_bucket: str
    s3_access_key: str
    s3_secret_key: str
    deployment_file: str
    git_repo: str
    git_pass: str
    local_repo: str

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
        "s3_url": os.environ.get('s3_url') if os.environ.get('s3_url') else "http://localhost:9000",
        "s3_bucket": os.environ.get('s3_bucket') if os.environ.get('s3_bucket') else "test",
        "s3_access_key": os.environ.get('s3_access_key') if os.environ.get('s3_access_key') else "minioadmin",
        "s3_secret_key": os.environ.get('s3_secret_key') if os.environ.get('s3_secret_key') else "minioadmin",
        "s3_region": os.environ.get('s3_region') if os.environ.get('s3_region') else "us-east-1",
        "deployment_file": os.environ.get('deployment_file') if os.environ.get('deployment_file') else "deployments.json",
        "git_repo": os.environ.get('git_repo') if os.environ.get('git_repo') else "",
        "git_pass": os.environ.get('git_pass') if os.environ.get('git_pass') else "password",
        "local_repo": os.environ.get('local_repo') if os.environ.get('local_repo') else "tmp"
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
