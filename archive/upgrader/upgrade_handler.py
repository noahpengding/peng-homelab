from app.handlers.deployment_handlers import get_deployment_by_name, save_deployment
from .upgrade import upgrade
import time
from app.utils.rabbitmq_publisher import RabbitMQPublisher
from app.utils.log import output_log

def upgrade_handler(app: str, name: str) -> None:
    app = get_deployment_by_name(app, name)
    if app:
        output_log(f"Upgrade handler for {app.get_deployment()}", "debug")
        app_info = app.get_deployment()
        if app_info["auto_upgrade"] and (not app_info["hold_flag"]):
            if app_info["current_version"] != app_info["latest_version"]:
                output_log(f"Upgrading {app_info['app']}.{app_info['name']} from {app_info['current_version']} to {app_info['latest_version']}", "info")
                new_app = upgrade(app)
                save_deployment(new_app)
                new_app_info = new_app.get_deployment()
                r = RabbitMQPublisher()
                message = f"### Upgrade {new_app_info['app']}.{new_app_info['name']} from {app_info['current_version']} to {new_app_info['current_version']}\n"
                message += f"Refer to the [document]({new_app_info['document_url']}) for more details."
                r.publish(message)
