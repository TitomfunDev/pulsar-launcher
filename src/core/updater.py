import os
import platform
import requests
import shutil
import subprocess
import sys
import tempfile
import uuid
import zipfile
from packaging.version import parse

try:
    from core.version import INTERNAL_TAG
except ImportError:
    INTERNAL_TAG = "v0.0.0-dev"

REPO_OWNER = "TitomfunDev"
REPO_NAME = "pulsar-launcher"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"

def check_and_update():
    is_compiled = getattr(sys, 'frozen', False)
    if not is_compiled:
        print("Dev mode enable. Update skipped.")
        return
    
    try:
        response = requests.get(GITHUB_API_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error checking for updates: {e}")
        return

    latest_tag = data.get("tag_name")
    if not latest_tag or parse(latest_tag) <= parse(INTERNAL_TAG):
        print("PulsarLauncher is up to date.")
        return

    print(f"Update available: {latest_tag} (current: {INTERNAL_TAG})")

    asset = find_matching_asset(data.get("assets", []))
    if not asset:
        print(f"No compatible binary found for {platform.system()} in release.")
        return

    download_and_apply_update(asset["browser_download_url"])

def find_matching_asset(assets):
    system = platform.system().lower()

    for asset in assets:
        name = asset["name"].lower()
        if system == "windows" and name.endswith("-windows.zip"):
            return asset
        elif system == "darwin" and name.endswith(".app.zip"):
            return asset
        elif system == "linux" and name.endswith("-linux"):
            return asset

    return None

def download_and_apply_update(download_url: str):
    temp_dir = tempfile.gettempdir()
    current_os = platform.system().lower()
    current_path = sys.executable

    print("Downloading update...")
    
    unique_id = uuid.uuid4().hex[:8]
    downloaded_file = os.path.join(temp_dir, f"pulsar_update_{unique_id}")

    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(downloaded_file, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    if current_os == "windows":
        
        extract_folder = os.path.join(temp_dir, f"pulsar_extracted_{unique_id}")
        if os.path.exists(extract_folder):
            shutil.rmtree(extract_folder)

        with zipfile.ZipFile(downloaded_file, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)

        current_app_dir = os.path.dirname(current_path)

        bat_path = os.path.join(temp_dir, f"update_pulsar_{unique_id}.bat")
        
        bat_content = f"""@echo off
echo PulsarLauncher updating... Please wait...
timeout /t 3 /nobreak >nul
echo Waiting for PulsarLauncher to close...
set /a count=0

:loop
tasklist | find /i "{os.path.basename(current_path)}" >nul
if errorlevel 1 goto apply_update

set /a count+=1
if %count% geq 15 (
    echo Killing PulsarLauncher process...
    taskkill /f /im "{os.path.basename(current_path)}" >nul 2>&1
    goto apply_update
)

timeout /t 1 /nobreak >nul
goto loop

:apply_update
echo Updating folder...
robocopy "{extract_folder}" "{current_app_dir}" /E /MOVE >nul

echo Waiting for file unlock...
timeout /t 2 /nobreak >nul

echo Launching new version...
start "" "{current_path}"
del "%~f0"
"""
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)

        os.startfile(bat_path)
        sys.exit(0)

    elif current_os == "linux":
        os.chmod(downloaded_file, 0o755)
        os.replace(downloaded_file, current_path)
        subprocess.Popen([current_path])
        sys.exit(0)

    elif current_os == "darwin":
        extract_folder = os.path.join(temp_dir, f"pulsar_mac_extract_{unique_id}")
        if os.path.exists(extract_folder):
            shutil.rmtree(extract_folder)

        with zipfile.ZipFile(downloaded_file, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)

        app_bundle_path = current_path
        while app_bundle_path and not app_bundle_path.endswith(".app"):
            parent = os.path.dirname(app_bundle_path)
            if parent == app_bundle_path:
                break
            app_bundle_path = parent

        if not app_bundle_path.endswith(".app"):
            print("Error: Could not locate current .app directory.")
            return

        new_app_path = os.path.join(extract_folder, "PulsarLauncher.app")

        sh_path = os.path.join(temp_dir, f"update_pulsar_{unique_id}.sh")
        sh_content = f"""#!/bin/bash
sleep 2
rm -rf "{app_bundle_path}"
cp -R "{new_app_path}" "{app_bundle_path}"
open "{app_bundle_path}"
rm -rf "{extract_folder}"
rm -- "$0"
"""
        with open(sh_path, "w", encoding="utf-8") as f:
            f.write(sh_content)

        os.chmod(sh_path, 0o755)
        subprocess.Popen(["/bin/bash", sh_path])
        sys.exit(0)