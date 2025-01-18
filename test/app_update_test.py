import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from app.services.updater import update
from app.models.deployment import Deployment

helm_deployment = Deployment(
    app="gitlab",
    name="gitlab-helm",
    argo_app="gitlab-helm",
    status="Running",
    image_url="https://charts.gitlab.io/",
    image_chart_name="gitlab",
    image_check_method="Helm",
    current_version="8.6.2",
    latest_version="8.6.2",
    target_version="latest",
    hold_flag=False,
    auto_update=True,
    auto_upgrade=True,
    changes=[{
        "file": "argo/applications/gitlab-helm.yaml",
        "key": "spec.source.targetRevision",
        "value": "8.6.2"
    }],
    document_url="test_image_url"
)

updated_helm = update.update_app(helm_deployment)
print(updated_helm.get_deployment())


docker_deployment = Deployment(
    app="immich",
    name="immich-server",
    argo_app="immich",
    status="Running",
    image_url="ghcr.io/immich-app",
    image_chart_name="immich-server",
    image_check_method="Docker",
    current_version="v1.121.0",
    latest_version="v1.121.0",
    target_version="release",
    hold_flag=False,
    auto_update=True,
    auto_upgrade=True,
    changes=[{
        "file": "immich/dp-server.yaml",
        "key": "spec.containers[0].image",
        "value": "ghcr.io/immich-app/immich-server:v1.121.0"
    }],
    document_url="test_image_url"
)

updated_docker = update.update_app(docker_deployment)
print(updated_docker.get_deployment())

docker_2_deployment = Deployment(
    app="vaultwarden",
    name="deployment-app",
    argo_app="vaultwarden",
    status="Running",
    image_url="",
    image_chart_name="vaultwarden/server",
    image_check_method="Docker",
    current_version="1.32.5",
    latest_version="1.32.5",
    target_version="latest",
    hold_flag=False,
    auto_update=True,
    auto_upgrade=True,
    changes=[{
        "file": "vaultwarden/deployment-app",
        "key": "spec.containers[0].image",
        "value": "vaultwarden/server:1.32.5"
    }],
    document_url="test_image_url"
)

updated_docker = update.update_app(docker_2_deployment)
print(updated_docker.get_deployment())

docker_3_deployment = Deployment(
    app="minio",
    name="deployment",
    argo_app="minio",
    status="Running",
    image_url="",
    image_chart_name="quay.io/minio/minio",
    image_check_method="Docker",
    current_version="RELEASE.2024-11-07T00-52-20Z",
    latest_version="RELEASE.2024-11-07T00-52-20Z",
    target_version="latest",
    hold_flag=False,
    auto_update=True,
    auto_upgrade=True,
    changes=[{
        "file": "vaultwarden/deployment-app",
        "key": "spec.containers[0].image",
        "value": "quay.io/minio/minio:RELEASE.2024-11-07T00-52-20Z"
    }],
    document_url="test_image_url"
)

updated_docker = update.update_app(docker_3_deployment)
print(updated_docker.get_deployment())
