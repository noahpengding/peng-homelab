from app.handlers.deployment_handlers import get_all_deployments, save_deployment
from .update import update_app
from app.utils.rabbitmq_publisher import RabbitMQPublisher
from app.models.deployment import Deployment
from app.utils.log import output_log

def update_all_handler() -> None:
    apps = get_all_deployments()
    for app in apps:
        update_handler(app)

def update_handler(app: Deployment) -> None:
    app_info = app.get_deployment()
    output_log(f"Checking for updates for {app_info["app"]}.{app_info["name"]}", "info")
    if app_info["status"] != "Stop" and app_info["auto_update"]:
        new_app = update_app(app)
        if new_app:
            output_log(f"New App information {new_app.get_deployment()}", "debug")
            save_deployment(new_app)
            new_app_info = new_app.get_deployment()
            output_log(f"Found New Version for {new_app_info["app"]}.{new_app_info["name"]}", "info")
            r = RabbitMQPublisher()
            message = f"### {new_app_info['app']}.{new_app_info["name"]} updated from {app_info["latest_version"]} to version {new_app_info['latest_version']} \n"
            message += f"The image url is {new_app_info["image_url"]}/{new_app_info["image_chart_name"]} \n"
            message += f"Refer to document in {new_app_info["document_url"]} \n"
            message += f"Press 'upgrade {new_app_info['app']}.{new_app_info['name']}' to upgrade the app \n"
            r.publish(message)
