import json
import ast
from .deployment_output import output_deployment_all, output_deployment_by_name
from .deployment_handlers import save_deployment, get_deployment_by_name
from app.services.upgrader.upgrade_handler import upgrade_handler
from app.models.deployment import Deployment
from app.services.updater.update_handler import update_all_handler, update_handler
from app.utils.log import output_log

def RabbitMQMessageHandler(data):
    data = json.loads(data.decode("utf-8"))["data"]
    message_type = data["type"]
    message = data["message"]
    output_log(f"Received {message_type} message: {message}", "info")
    if message_type == "get_app":
        if message == "all":
            output_deployment_all()
        else:
            app, name = message.split(".")
            output_deployment_by_name(app, name)
    if message_type == "upgrade":
        app, name = message.split(".")
        upgrade_handler(app, name)
    if message_type == "set_app":
        if (type(message) == str):
            message = ast.literal_eval(message.replace("null", "None").replace("true", "True").replace("false", "False"))
        new_deployment = Deployment(**message)
        save_deployment(new_deployment)
    if message_type == "update":
        if message == "all":
            update_all_handler()
        else:
            app, name = message.split(".")
            update_handler(get_deployment_by_name(app, name))
