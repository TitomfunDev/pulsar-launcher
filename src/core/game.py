# External dependencies
import subprocess
import minecraft_launcher_lib as mll

# Pulsar dependencies
from core import paths, auth, instances, java_manager

def _make_options(instance_id: str) -> dict:
    login_data = auth.get_valid_session()
    
    instance_info = instances.get_instance_infos(instance_id)
    java_config = instance_info.get("java")
    java_version = java_config.get("version")
    
    java_exe = java_manager.find_java_executable(java_version)
    
    options = {
        "username": login_data["name"], 
        "uuid": login_data["id"], 
        "token": login_data["access_token"]
    }
    
    if java_exe:
        options["executablePath"] = java_exe
        
    return options


def _make_command(instance_id: str) -> list[str]:
    version_id = instances.get_version(instance_id)
    game_dir = paths.get_selected_instance_dir(instance_id)
    options = _make_options(instance_id)

    return mll.command.get_minecraft_command(
        version_id, 
        game_dir, 
        options
    )


def launch(instance_id: str):
    instances.install_instance(instance_id)

    command = _make_command(instance_id)
    subprocess.run(command, cwd=paths.get_selected_instance_dir(instance_id))