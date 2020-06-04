"""
Common constants used by configurer & jupyterhub_config.py
"""

import os
import pathlib


HERE = pathlib.Path(__file__).absolute().parent

# We require a version of python installed via conda
CONDA_DIR = pathlib.Path(os.environ['CONDA_DIR'])
CONFIG_DIR = CONDA_DIR / "etc/jupyterhub"
STATE_DIR = CONDA_DIR / "var/jupyterhub"
BIN_DIR = CONDA_DIR / "bin"
JUPYTERHUB_CONFIG_D_DIR = CONFIG_DIR / "jupyterhub_config.d"

# Shared credentials between traefik proxy & JupyterHub
TRAEFIK_CREDS_PATH = CONDA_DIR / "etc/jupyterhub/traefik-creds.json"

# The miniforge installer file
MINIFORGE_INSTALLER_PATH = CONDA_DIR / "share/jupyterhub/miniforge-installer.sh"
MINIFORGE_VERSION = "4.8.3-2"
MINIFORGE_URL = f"https://github.com/conda-forge/miniforge/releases/download/{MINIFORGE_VERSION}/Miniforge3-{MINIFORGE_VERSION}-Linux-x86_64.sh"

# environment.yml used to install base notebook + dependencies
NOTEBOOK_ENVIRONMENT_YML = HERE / "notebook-environment.yml"