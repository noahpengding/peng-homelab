from app.models.deployment import Deployment
from app.utils.log import output_log
from .docker_checker import DockerChecker
from .helm_checker import HelmChecker


def update_app(app: Deployment) -> Deployment:
    app_info = app.get_deployment()
    match app_info["image_check_method"]:
        case "Docker":
            d = DockerChecker()
            url_prefix = app_info["image_url"] + "/" if app_info["image_url"] else ""
            current_version = (
                url_prefix
                + app_info["image_chart_name"]
                + ":"
                + app_info["latest_version"]
            )
            target_version = (
                url_prefix
                + app_info["image_chart_name"]
                + ":"
                + app_info["target_version"]
            )
            if not d.check_image(current_version, target_version):
                image_tag = d.pull_image_version(target_version)
                latest_version = _get_version(image_tag, target_version)
                if latest_version:
                    app.update(latest_version)
                    return app
        case "Helm":
            h = HelmChecker()
            if not h.check_helm(
                app_info["image_url"],
                app_info["image_chart_name"],
                app_info["latest_version"],
            ):
                new_version = h.pull_helm_version(
                    app_info["image_url"], app_info["image_chart_name"]
                )
                app.update(new_version)
                return app
    return None


def _get_version(image_data: dict, target_version: str) -> str:
    if image_data["RepoTags"]:
        for tag in image_data["RepoTags"]:
            if tag != target_version:
                return tag
    if image_data["Config"]["Labels"]:
        for label in image_data["Config"]["Labels"]:
            if label == "org.opencontainers.image.version":
                return image_data["Config"]["Labels"][label]
            if label == "version":
                return image_data["Config"]["Labels"][label]
    output_log(f"Cannot find version for {image_data}", "error")
    return ""
