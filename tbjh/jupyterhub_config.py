import os
import pathlib
from glob import glob
from jupyterhub_traefik_proxy import TraefikTomlProxy

# We require a version of python installed via conda
CONDA_DIR = pathlib.Path(os.environ['CONDA_DIR'])

# Don't kill servers when JupyterHub restarts
c.JupyterHub.cleanup_servers = False

c.JupyterHub.proxy_class = TraefikTomlProxy
c.TraefikTomlProxy.should_start = True

# Load arbitrary .py config files if they exist.
# This is our escape hatch
extra_configs = sorted(glob(os.path.join(CONDA_DIR, 'etc', 'jupyterhub_config.d', '*.py')))
for ec in extra_configs:
    load_subconfig(ec)