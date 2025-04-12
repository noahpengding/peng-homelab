from app.models.deployment import Deployment
from app.utils.minio_connection import MinioStorage
from app.config.config import config
from app.utils.log import output_log
import json
import os


def get_all_deployments() -> list:
    m = MinioStorage()
    m.file_download(config.deployment_file, "tmp.json")
    deployment_json = json.load(open("tmp.json"))
    os.remove("tmp.json")
    if deployment_check(deployment_json):
        return [Deployment(**deployment) for deployment in deployment_json]


def get_deployment_by_name(app: str, name: str) -> Deployment:
    m = MinioStorage()
    m.file_download(config.deployment_file, "tmp.json")
    deployment_json = json.load(open("tmp.json"))
    os.remove("tmp.json")
    for deployment in deployment_json:
        try:
            if deployment["app"] == app and deployment["name"] == name:
                return Deployment(**deployment)
        except Exception:
            continue
    return None


def deployment_check(deployment):
    for deploy in deployment:
        try:
            Deployment(**deploy)
            return True
        except Exception as e:
            output_log(f"Deployment check failed: {e}", "error")
            return False


def save_deployment(deployment: Deployment) -> None:
    m = MinioStorage()
    deployment_json = []
    if m.file_exists(config.deployment_file):
        m.file_download(config.deployment_file, "tmp.json")
        deployment_json = json.load(open("tmp.json"))
        for deploy in deployment_json:
            if deploy["name"] == deployment.name:
                deployment_json.remove(deploy)
                break
    else:
        open("tmp.json", "w").close()
    output_log(f"Getting deployment: {deployment_json}", "debug")
    output_log(f"Saving deployment: {deployment.get_deployment()}", "debug")
    deployment_json.append(deployment.get_deployment())
    if deployment_check(deployment_json):
        with open("tmp.json", "w") as f:
            json.dump(deployment_json, f)
        m.file_upload("tmp.json", config.deployment_file, "application/json")
