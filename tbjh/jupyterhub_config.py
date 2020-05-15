import json
import os
import pathlib
from glob import glob
from jupyterhub_traefik_proxy import TraefikTomlProxy

# We require a version of python installed via conda
CONDA_DIR = pathlib.Path(os.environ['CONDA_DIR'])

# Don't kill servers when JupyterHub restarts
c.JupyterHub.cleanup_servers = False

# Traefik should be started by systemd
c.JupyterHub.proxy_class = TraefikTomlProxy
c.TraefikTomlProxy.should_start = False

# FIXME: This needs to be heavily de-duped
traefik_creds_path = CONDA_DIR / "etc/jupyterhub/traefik-creds.json"
with open(traefik_creds_path) as f:
    creds = json.load(f)

if 'version' not in creds or creds['version'] != 'v1':
    # FIXME: Better error message
    raise ValueError("Invalid traefik-creds.json file")

c.TraefikTomlProxy.traefik_api_username = creds['username']
c.TraefikTomlProxy.traefik_api_password = creds['password']


# Load arbitrary .py config files if they exist.
# This is our escape hatch
extra_configs = sorted(glob(os.path.join(CONDA_DIR, 'etc', 'jupyterhub', 'jupyterhub_config.d', '*.py')))
for ec in extra_configs:
    load_subconfig(ec)