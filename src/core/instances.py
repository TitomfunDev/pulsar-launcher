# External dependencies
import json
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Pulsar dependencies
from core import paths, download, java_manager


# Variables
MANIFEST_URL = "https://cdn.titomfun.fr/launcher/manifest.json"
LOCAL_MANIFEST_PATH = Path(paths.get_launcher_dir()) / "manifest.json"


def _load_local_manifest() -> dict | None:
    if LOCAL_MANIFEST_PATH.exists():
        try:
            return json.loads(LOCAL_MANIFEST_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
    return None


def _save_local_manifest(manifest: dict) -> None:
    LOCAL_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), 
        encoding="utf-8"
    )


class DeprecatedFeatureError(Exception):
    pass


def sync_and_get_manifest() -> dict:
    local_manifest = _load_local_manifest()
    remote_manifest = download.fetch_instance_manifest(MANIFEST_URL)

    if remote_manifest is None:
        if local_manifest is not None:
            return local_manifest
        raise RuntimeError("Aucune connexion réseau et aucun manifeste local disponible.")

    if local_manifest is None:
        _save_local_manifest(remote_manifest)
        return remote_manifest

    local_version = local_manifest.get("manifest_version", 0)
    remote_version = remote_manifest.get("manifest_version", 0)

    if remote_manifest.get("deprecated", True):
        raise DeprecatedFeatureError("Manifest feature deprecated.")

    if remote_version == 0 or remote_version > local_version:
        _save_local_manifest(remote_manifest)
        return remote_manifest

    return local_manifest


def get_all_event_instances() -> list[str]:
    local_manifest = _load_local_manifest() or {}
    instances = local_manifest.get("instances", [])
    return [instance["id"] for instance in instances if "id" in instance]


def get_instance_infos(instance_id: str) -> dict:
    local_manifest = _load_local_manifest() or {}
    instances = local_manifest.get("instances", [])

    for instance in instances:
        if instance.get("id") == instance_id:
            return instance
            
    return {}


def get_version(instance_id: str) -> str:
    instance = get_instance_infos(instance_id)
    if not instance:
        raise ValueError(f"Instance '{instance_id}' introuvable.")

    mc_config = instance.get("minecraft", {})
    mc_version = mc_config.get("version", "")
    loader = mc_config.get("loader")

    if not loader:
        return mc_version

    loader_type = loader.get("type", "").lower()
    loader_version = loader.get("version", "")

    # Naming convention for minecraft_launcher_lib
    if loader_type == "fabric":
        return f"fabric-loader-{loader_version}-{mc_version}"
    elif loader_type == "quilt":
        return f"quilt-loader-{loader_version}-{mc_version}"
    elif loader_type == "forge":
        return f"{mc_version}-forge-{loader_version}"
    elif loader_type == "neoforge":
        return f"neoforge-{loader_version}"

    return mc_version


def install_instance(instance_id: str) -> bool:
    instance = get_instance_infos(instance_id)
    if not instance:
        return False

    instance_folder = Path(paths.get_selected_instance_dir(instance_id))
    version_file_path = instance_folder / "version.txt"
    version = None

    java_config = instance.get("java") or {}
    java_version = java_config.get("version", 17)
    java_exe = java_manager.find_java_executable(java_version)

    if not java_exe:
        print("Java portable introuvable. Installation de Java requise avant l'instance...")
        success = java_manager.install_java(java_version)
        if not success:
            raise RuntimeError("Échec critique de l'installation de Java.")
        java_exe = java_manager.find_java_executable(java_version)

    if java_exe:
        java_bin_dir = str(Path(java_exe).parent)
        if java_bin_dir not in os.environ["PATH"]:
            os.environ["PATH"] = java_bin_dir + os.pathsep + os.environ["PATH"]

    instance_up_to_date = False
    try:
        with open(version_file_path, "r", encoding="utf-8") as fichier:
            version = int(fichier.read().strip())
            if version >= instance["instance_version"] :
                instance_up_to_date = True
    except (FileNotFoundError, ValueError):
        pass

    if instance_up_to_date:
        return True

    mc_config = instance["minecraft"]
    loader_config = mc_config.get("loader")
    loader_type = loader_config.get("type") if loader_config else None
    loader_version = loader_config.get("version") if loader_config else None
    downloads = instance.get("downloads") or {}

    max_tasks = 1 + len(downloads)
           
    with ThreadPoolExecutor(max_workers=max_tasks) as executor:
        futures = []

        futures.append(
            executor.submit(
                download.install_minecraft, mc_config["version"], instance_id, loader_type, loader_version
            )
        )
        for category, data in downloads.items():
            if isinstance(data, dict) and "url" in data and "sha256" in data:
                futures.append(
                    executor.submit(download.download_ressources, data["url"], data["sha256"], instance_id, category)
                )

        for future in futures:
            future.result()

    instance_folder.mkdir(parents=True, exist_ok=True)
    version_file_path.write_text(str(instance["instance_version"]), encoding="utf-8")

    return True