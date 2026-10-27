# External dependencies
import platform
from pathlib import Path

# Pulsar dependencies
from core import download,paths,system_info
    

def install_java(version):

    java_path = paths.get_java_path()

    release_type = "ga"
    os_name = system_info.get_system_name()
    arch = system_info.get_system_architecture()
    image_type = "jre"
    jvm_impl = "hotspot"
    heap_size = "normal"
    vendor = "eclipse"

    url = f"https://api.adoptium.net/v3/binary/latest/{version}/{release_type}/{os_name}/{arch}/{image_type}/{jvm_impl}/{heap_size}/{vendor}"

    download.download_java(url, java_path, version, os_name)

def find_java_executable(java_version: int) -> str:
    base_path = Path(paths.get_java_path())
    
    if not base_path.exists():
        return None

    is_windows = platform.system().lower() == "windows"
    target_exe = "javaw.exe" if is_windows else "java"

    for folder in base_path.iterdir():
        if folder.is_dir():
            if f"jdk-{java_version}" in folder.name or folder.name.startswith(str(java_version)):
                for exe in folder.rglob(target_exe):
                    return str(exe)

    return None