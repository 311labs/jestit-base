"""
Project Path Configuration Script

This script dynamically sets up the project's directory structure and ensures all necessary paths
are correctly added to `sys.path`. It is used to:
- Define key project paths (e.g., ROOT, VAR_PATH, DJANGO_ROOT).
- Dynamically load additional modules from `.site_packages`.
- Automatically include app directories from the `apps/` folder.
- Configure Python's import path (`sys.path`) to recognize these locations.

This ensures that all project modules and dependencies are properly recognized
without hardcoding absolute paths.
"""
import sys
from pathlib import Path

# Resolve paths
FILE = Path(__file__).resolve()
ROOT = FILE.parent.parent
PROJECT_NAME = ROOT.name.upper()

# Define key paths
DJANGO_ROOT = ROOT / "django"
VER_FILE = DJANGO_ROOT / "version.py"
VAR_PATH = ROOT / "var"
EXTRA_MODULES = ROOT / "packages"
SETTINGS_PATH = ROOT / "config"

# Add key directories to sys.path
sys.path.insert(0, str(DJANGO_ROOT))
sys.path.insert(0, str(EXTRA_MODULES))
sys.path.insert(0, str(SETTINGS_PATH))

# Load additional site-packages paths from .site_packages file
SITE_PACKAGES_FILE = ROOT / ".site_packages"

if SITE_PACKAGES_FILE.exists():
    with SITE_PACKAGES_FILE.open("r") as f:
        site_packages_paths = [path.strip() for path in f.readlines() if path.strip()]
    for path in site_packages_paths:
        site_path = Path(path)
        if site_path.exists() and str(site_path) not in sys.path:
            sys.path.insert(0, str(site_path))

# Load app directories dynamically
APPS_PATH = ROOT / "apps"
APP_FOLDERS = []

def load_apps():
    if APPS_PATH.exists():
        for item in APPS_PATH.iterdir():
            if item.is_dir() and str(item) not in sys.path:
                APP_FOLDERS.append(str(item))
                sys.path.append(str(item))
    return APP_FOLDERS


def init_django():
    import django
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project')
    load_apps()
    django.setup()
