from git import Repo
from app.config.config import config
from app.models.deployment import Deployment
from app.models.changes import Changes
import yaml
import os
import time
from datetime import datetime
from app.utils.log import output_log

def upgrade(app: Deployment) -> Deployment:
    output_log(f"Upgrade handler for {config.local_repo} | {config.git_repo} | {config.git_pass}", "debug")
    if os.path.exists(config.local_repo):
        repo = Repo(config.local_repo)
        repo.remotes.origin.pull()
    else:
        repo = Repo.clone_from(
        config.git_repo.replace("https://", f"https://oauth2:{config.git_pass}@"),
        config.local_repo
    )
    repo.config_writer().set_value("user", "email", "bot@dingyipeng.com").release()
    repo.config_writer().set_value("user", "name", "Bot").release()

    app_info = app.get_deployment()
    for change in app_info["changes"]:
        new_change = _update_file(config.local_repo, change, app_info["current_version"], app_info["latest_version"])
        app.modify_changes(new_change)
        app.upgrade(app_info["latest_version"])
    repo.git.add(update=True)
    commit_subject = f"Upgrade {app_info['name']} to {app_info["latest_version"]}"
    commit_body = f"Upgrade {app_info['name']} in App {app_info['app']} from {app_info["current_version"]} to {app_info["latest_version"]} at {datetime.now()}"
    repo.index.commit(f"{commit_subject}\n\n{commit_body}")
    repo.remote(name="origin").push()
    time.sleep(5)
    return app

def _update_file(local_location: str, change: dict, old_version:str, new_version: str) -> Changes:
    try:
        with open(f"{local_location}/{change["file"]}", "r") as f:
            data = list(yaml.safe_load_all(f))
        data_remain = data[1:] if len(data) >= 1 else []
        data = data[0] if len(data) >= 1 else data
        original_value = change["value"]
        change["value"] = original_value.replace(old_version, new_version)
        target = data
        keys = change["key"].split(".")
        for key in keys[:-1]:
            key = key.replace("[", "").replace("]", "")
            target = target[int(key)] if key.isdigit() else target[key]
        target[keys[-1]] = change["value"]
        with open(f"{local_location}/{change['file']}", "w") as f:
            yaml.dump_all([data] + data_remain, f, default_flow_style=False, explicit_start=True)
        return Changes(**change)
    except Exception as e:
        output_log(f"Error in updating file {change['file']} in {local_location} from {old_version} to {new_version}: {e}", "error")
        return Changes(**change)
