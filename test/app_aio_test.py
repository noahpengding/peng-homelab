import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from app.services.upgrader.upgrade_handler import upgrade_handler
from app.models.deployment import Deployment
from app.services.updater.update_handler import update_all_handler
from app.handlers.deployment_handlers import save_deployment

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
        "key": "spec.sources.0.targetRevision",
        "value": "8.6.2"
    }],
    document_url="test_image_url"
)

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
        "key": "spec.template.spec.containers.0.image",
        "value": "ghcr.io/immich-app/immich-server:v1.121.0"
    }],
    document_url="test_image_url"
)

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
        "file": "vaultwarden/deployment-app.yaml",
        "key": "spec.template.spec.containers.0.image",
        "value": "vaultwarden/server:1.32.5"
    }],
    document_url="test_image_url"
)

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
        "file": "minio/deployment.yaml",
        "key": "spec.template.spec.containers.0.image",
        "value": "quay.io/minio/minio:RELEASE.2024-11-07T00-52-20Z"
    }],
    document_url="test_image_url"
)

save_deployment(helm_deployment)
save_deployment(docker_deployment)
save_deployment(docker_2_deployment)
save_deployment(docker_3_deployment)

time.sleep(5)
update_all_handler()
time.sleep(5)

# upgrade_handler("gitlab", "gitlab-helm")
# upgrade_handler("immich", "immich-server")
# upgrade_handler("vaultwarden", "deployment-app")
# upgrade_handler("minio", "deployment")
