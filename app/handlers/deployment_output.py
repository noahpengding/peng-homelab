from .deployment_handlers import get_all_deployments, get_deployment_by_name
from app.utils.rabbitmq_publisher import RabbitMQPublisher

def _deployments_message(deployments: list) -> str:
    if deployments == []:
        return "### No deployments found"
    message = "### Here are all the deployments:\n"
    message += "| App_Name | Status | Image | Current Version | Latest Version | Hold | Auto_Update | Auto Upgrade| Document URL|\n"
    message += "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
    for deployment in deployments:
        deployment_info = deployment.get_deployment()
        message += f"| {deployment_info["app"] + '.' + deployment_info["name"]} "
        message += f"| {deployment_info["status"]} "
        message += f"| {deployment_info["image_url"] + '/' + deployment_info["image_chart_name"]} "
        message += f"| {deployment_info["current_version"]} "
        message += f"| {deployment_info["latest_version"]} "
        message += f"| {deployment_info["hold_flag"]} "
        message += f"| {deployment_info["auto_update"]} "
        message += f"| {deployment_info["auto_upgrade"]} "
        message += f"| {deployment_info["document_url"]} |\n"
    return message

def output_deployment_all() -> None:
    deployments = get_all_deployments()
    message = _deployments_message(deployments)
    m = RabbitMQPublisher()
    m.publish(message)
    m.close()

def output_deployment_by_name(app:str, name: str) -> None:
    deployment = get_deployment_by_name(app, name)
    message = _deployments_message([deployment])
    m = RabbitMQPublisher()
    m.publish(message)
    m.close()
