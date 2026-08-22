import hashlib
import minecraft_launcher_lib as mll
import os
import requests
import zipfile
from . import paths
from pathlib import Path

def fetch_instance_manifest(url: str) -> dict | None:
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        return None

def download_and_extract_zip(download_url: str, expected_hash: str, instance_id: str):
    instance_dir = Path(paths.get_current_instance_dir(instance_id))
    instance_dir.mkdir(parents=True, exist_ok=True)
    
    zip_path = instance_dir / "temp_download.zip"

    response = requests.get(download_url, stream=True, timeout=30)
    response.raise_for_status()

    hasher = hashlib.sha256()

    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                hasher.update(chunk)

    if expected_hash and hasher.hexdigest().lower() != expected_hash.lower():
        if zip_path.exists():
            os.remove(zip_path)
        raise ValueError("Archive corrompue : l'empreinte SHA256 ne correspond pas.")

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(instance_dir)
    finally:
        os.remove(zip_path)    

def install_minecraft(version: str, instance_id: str, loader_type: str | None = None, loader_version: str | None = None) -> None:
    instance_dir = paths.get_current_instance_dir(instance_id)

    if not loader_type or loader_type.lower() == "vanilla":
        mll.install.install_minecraft_version(version, instance_dir)
        return

    loader = loader_type.lower()
    forge =  mll.mod_loader.get_mod_loader("forge")
    neoforge =  mll.mod_loader.get_mod_loader("neoforge")
    fabric =  mll.mod_loader.get_mod_loader("fabric")
    quilt =  mll.mod_loader.get_mod_loader("quilt")
    
    if loader == "fabric":
        fabric.install(version, instance_dir, loader_version=loader_version)
        
    elif loader == "forge":
        forge.install(version, instance_dir, loader_version=loader_version)
        
    elif loader == "quilt":
        quilt.install(version, instance_dir, loader_version=loader_version)
        
    elif loader == "neoforge":
        neoforge.install(version, instance_dir, loader_version=loader_version)
        
    else:
        raise ValueError(f"Modloader inconnu ou non pris en charge : {loader_type}")
