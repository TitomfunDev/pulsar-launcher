import subprocess
import minecraft_launcher_lib as mll
from . import paths
from . import download
from . import auth
from . import instances

def _make_options() -> dict:
    login_data = auth.get_valid_session()
    
    options = {"username": login_data["name"], "uuid": login_data["id"], "token": login_data["access_token"], }
    return options


def _make_command(instance_id: str) -> list[str]:
    version_id = instances.get_version(instance_id)
    game_dir = paths.get_current_instance_dir(instance_id)
    options = _make_options()

    return mll.command.get_minecraft_command(
        version_id, 
        game_dir, 
        options
    )


def launch(instance_id: str):
    instances.install_instance(instance_id)

    command = _make_command(instance_id)
    subprocess.run(command, cwd=paths.get_current_instance_dir(instance_id))