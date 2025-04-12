import uuid
from datetime import datetime
from .changes import Changes
from app.utils.log import output_log


class Deployment:
    def __init__(self, **kwargs):
        self.id = str(uuid.uuid4())
        self.app = kwargs.get("app")
        self.name = kwargs.get("name")
        self.argo_app = (
            kwargs.get("argo_app") if kwargs.get("argo_app") else kwargs.get("app")
        )
        self.status = kwargs.get("status") if kwargs.get("status") else "Unknown"
        self.image_url = kwargs.get("image_url") if kwargs.get("image_url") else ""
        self.image_chart_name = (
            kwargs.get("image_chart_name") if kwargs.get("image_chart_name") else ""
        )
        self.image_check_method = (
            kwargs.get("image_check_method")
            if kwargs.get("image_check_method")
            else "Docker"
        )
        self.current_version = (
            kwargs.get("current_version") if kwargs.get("current_version") else ""
        )
        self.latest_version = (
            kwargs.get("latest_version") if kwargs.get("latest_version") else ""
        )
        self.target_version = (
            kwargs.get("target_version") if kwargs.get("target_version") else "latest"
        )
        self.hold_flag = kwargs.get("hold_flag") if kwargs.get("hold_flag") else False
        self.auto_update = (
            kwargs.get("auto_update") if kwargs.get("auto_update") else True
        )
        self.auto_upgrade = (
            kwargs.get("auto_upgrade") if kwargs.get("auto_upgrade") else True
        )
        self.changes = (
            [Changes(**change) for change in kwargs.get("changes")]
            if kwargs.get("changes")
            else []
        )
        self.document_url = (
            kwargs.get("document_url")
            if kwargs.get("document_url")
            else kwargs.get("image_url")
        )
        self.last_upgrade = (
            datetime.strptime(kwargs.get("last_upgrade"), "%m/%d/%Y, %H:%M:%S")
            if kwargs.get("last_upgrade")
            else datetime.now()
        )
        self.last_update = (
            datetime.strptime(kwargs.get("last_upgrade"), "%m/%d/%Y, %H:%M:%S")
            if kwargs.get("last_update")
            else datetime.now()
        )

    def update(self, version: str) -> None:
        self.latest_version = version
        self.last_update = datetime.now()

    def upgrade(self, version: str) -> None:
        self.current_version = version
        self.last_upgrade = datetime.now()

    def hold(self) -> None:
        self.hold_flag = True

    def release(self) -> None:
        self.hold_flag = False

    def add_changes(self, new_changes: str) -> None:
        if new_changes not in self.changes:
            self.changes.append(new_changes)

    def modify_changes(self, change: Changes) -> None:
        output_log(f"Modifying {change.file} with {change.key}", "debug")
        for i, c in enumerate(self.changes):
            output_log(f"Checking {c.file} with {c.key}", "debug")
            if c.file == change.file and c.key == change.key:
                self.changes[i] = change

    def set_status(self, status: str) -> None:
        self.status = status

    def set_target(self, target_version: str) -> None:
        self.target_version = target_version

    def set_auto_update(self, auto_update: bool) -> None:
        self.auto_update = auto_update

    def set_auto_upgrade(self, auto_upgrade: bool) -> None:
        self.auto_upgrade = auto_upgrade

    def get_deployment(self) -> dict:
        return {
            "id": self.id,
            "app": self.app,
            "name": self.name,
            "argo_app": self.argo_app,
            "status": self.status,
            "image_url": self.image_url,
            "image_chart_name": self.image_chart_name,
            "image_check_method": self.image_check_method,
            "current_version": self.current_version,
            "latest_version": self.latest_version,
            "target_version": self.target_version,
            "hold_flag": self.hold_flag,
            "auto_update": self.auto_update,
            "auto_upgrade": self.auto_upgrade,
            "changes": [change.get_changes() for change in self.changes],
            "document_url": self.document_url,
            "last_upgrade": self.last_upgrade.strftime("%m/%d/%Y, %H:%M:%S"),
            "last_update": self.last_update.strftime("%m/%d/%Y, %H:%M:%S"),
        }
