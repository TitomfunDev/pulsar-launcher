from pathlib import Path
from platformdirs import user_data_dir

data_path_str = user_data_dir(
    appname="TitomfunLauncher", 
    appauthor=False, 
    roaming=True
)

DATA_DIR = Path(data_path_str)

def get_launcher_dir() -> str:
    return DATA_DIR

def get_instance_dir() -> str:
    return str(DATA_DIR / "instances")

def get_current_instance_dir(current_event: str) -> str:
    return str(DATA_DIR / "instances" / current_event)
