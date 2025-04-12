import docker
from app.utils.log import output_log


class DockerChecker:
    def __init__(self):
        self.client = docker.from_env()

    def _pull_image_id(self, image_name) -> str:
        image = self.client.images.pull(image_name)
        return image.id

    def pull_image_version(self, image_name) -> str:
        image = self.client.images.pull(image_name)
        output_log(f"Image pulled: {image}", "debug")
        return image.attrs

    def check_image(self, current_version, target_version) -> bool:
        try:
            current_image = self._pull_image_id(current_version)
            target_image = self._pull_image_id(target_version)
            return current_image == target_image
        except Exception as e:
            output_log(f"Error: {e}", "error")
            return True
