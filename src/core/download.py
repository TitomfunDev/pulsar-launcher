# External dependencies
import hashlib
import minecraft_launcher_lib as mll
import os
import requests
import shutil
import tarfile
import zipfile
from pathlib import Path

# Pulsar dependencies
from core import paths

def fetch_instance_manifest(url: str) -> dict | None:
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        return None

def download_ressources(download_url: str, expected_hash: str, instance_id: str, category: str):
    instance_dir = Path(paths.get_selected_instance_dir(instance_id))
    target_dir = instance_dir / category
    
    if target_dir.exists():
        shutil.rmtree(target_dir)
    
    target_dir.mkdir(parents=True, exist_ok=True)

    zip_path = instance_dir / f"temp_{category}.zip"

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
        raise ValueError("Corrupted archive : SHA256 fingerprint doesn't match.")

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(target_dir)
    finally:
        if zip_path.exists():
            os.remove(zip_path)

def install_minecraft(version: str, instance_id: str, loader_type: str | None = None, loader_version: str | None = None) -> None:
    instance_dir = paths.get_selected_instance_dir(instance_id)

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
        raise ValueError(f"Unknown modloader: {loader_type}")


def download_java(url, path, version, os_name):
    try:

        os.makedirs(path, exist_ok=True)
        response = requests.get(url, allow_redirects=True, stream=True)

        if response.status_code == 200:

            filename = response.url.split("/")[-1].split("?")[0]
            content_disposition = response.headers.get("content-disposition")
            if content_disposition and "filename=" in content_disposition:
                filename = (content_disposition.split("filename=")[1].strip('"\'').split(";")[0])

            if not filename or "." not in filename:
                filename = (f"java_{version}_{os_name}.zip" if os_name == "windows" else f"java_{version}_{os_name}.tar.gz")

            archive_path = os.path.join(path, filename)

            with open(archive_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            if filename.endswith(".zip"):
                with zipfile.ZipFile(archive_path, "r") as zip_ref:
                    zip_ref.extractall(path)
            elif filename.endswith(".tar.gz") or filename.endswith(".tgz"):
                with tarfile.open(archive_path, "r:gz") as tar_ref:
                    tar_ref.extractall(path)

            os.remove(archive_path)
            return True
        else:
            print(
                f"Error during request: HTTP code {response.status_code} -"
                f" {response.reason}"
            )
            return False

    except Exception as e:
        print(f"Error : {e}")
        return False