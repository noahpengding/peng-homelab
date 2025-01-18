import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.utils.rabbitmq_publisher import RabbitMQPublisher

m = RabbitMQPublisher()
message1 = {
    "type": "get_app",
    "message": "all"
}
message2 = {
    "type": "upgrade",
    "message": "traefik.traefik-helm"
}
message3 = {
    "type": "set_app",
    "message": {
        "app": "arr",
        "name": "dp-jellyseer",
        "argo_app": "arr",
        "status": "Running",
        "image_url": "",
        "image_chart_name": "fallenbagel/jellyseerr",
        "image_check_method": "Docker",
        "current_version": "2.2.0",
        "latest_version": "2.2.0",
        "target_version": "latest",
        "hold_flag": False,
        "auto_update": True,
        "auto_upgrade": True,
        "changes": [{
            "file": "arr/dp-jellyseer.yaml",
            "key": "spec.template.spec.containers.0.image",
            "value": "2.2.0"
        }],
        "document_url": "https://github.com/Fallenbagel/jellyseerr/blob/develop/CHANGELOG.md"
    }
}
message4 = {
    "type": "update",
    "message": "all"
}
m.publish(message4, "homelab")
m.close()
