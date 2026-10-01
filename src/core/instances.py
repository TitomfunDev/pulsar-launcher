import json
from pathlib import Path
from . import paths
from . import download

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
        raise DeprecationWarning

    if remote_version == 0 or remote_version > local_version:
        _save_local_manifest(remote_manifest)
        return remote_manifest

    return local_manifest

def get_all_instances() -> list[str]:
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
    """Retourne l'ID exact de la version tel que généré par minecraft_launcher_lib."""
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

    # Conventions de nommage de minecraft_launcher_lib
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

    mc_config = instance["minecraft"]
    loader_config = mc_config.get("loader")
    loader_type = loader_config.get("type") if loader_config else None
    loader_version = loader_config.get("version") if loader_config else None
    mods = instance.get("mods")
    config = instance.get("config")

    download.install_minecraft(mc_config["version"], instance_id, loader_type, loader_version)

    if mods is not None:
        download.download_and_extract_zip(mods["url"], mods["sha256"], instance_id)

    if config is not None:
        download.download_and_extract_zip(config["url"], config["sha256"], instance_id)

    return True