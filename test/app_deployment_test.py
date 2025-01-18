import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import app.handlers.deployment_handlers as deployment_handlers
import app.models.deployment as deployment
import app.models.changes as changes

new_deployment = deployment.Deployment(
    app="gitlab",
    name="gitlab-helm",
    argo_app="gitlab-helm",
    status="Running",
    image_url="https://charts.gitlab.io/",
    image_check_method="Helm",
    current_version="gitlab:8.6.2",
    latest_version="gitlab:8.6.2",
    target_version="gitlab:latest",
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

deployment_handlers.save_deployment(new_deployment)
deployments = deployment_handlers.get_all_deployments()
for d in deployments:
    print(d.get_deployment())
deploy = deployment_handlers.get_deployment_by_name("gitlab-helm")
print(deploy.get_deployment())
