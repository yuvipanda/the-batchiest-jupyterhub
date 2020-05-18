import json
import pwd
import os
import pathlib
import asyncio
import subprocess
from glob import glob
from jupyterhub_traefik_proxy import TraefikTomlProxy

HERE = pathlib.Path(__file__).absolute().parent

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

async def check_call_process(cmd):
    """
    Asynchronously execute a process, throw an error when it fails
    """
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(
            returncode=proc.returncode,
            cmd=cmd,
            stderr=stderr,
            output=stdout
        )

MINIFORGE_INSTALLER_PATH = CONDA_DIR / "share/jupyterhub/miniforge-installer.sh"
NOTEBOOK_ENVIRONMENT_YML = HERE / "notebook-environment.yml"


# Make sure there's a conda install
async def pre_spawn_hook(spawner):
    username = spawner.user.name
    homedir = pathlib.Path(pwd.getpwnam(username).pw_dir)
    if (homedir / 'conda').exists():
        # If 'conda' dir exists, assume we are good
        # In the future, we might have more sophisticated checks
        return

    # Install miniforge
    # FIXME: Show this as progress in spawn call
    await check_call_process([
        '/bin/sh',
        str(MINIFORGE_INSTALLER_PATH),
        '-b', '-p', str(homedir / 'conda'),
    ])

    # Install packages we want
    await check_call_process([
        str(homedir / 'conda/bin/conda'),
        'env', 'create',
        '-f', str(NOTEBOOK_ENVIRONMENT_YML)
    ])

c.Spawner.pre_spawn_hook = pre_spawn_hook
# Load arbitrary .py config files if they exist.
# This is our escape hatch
extra_configs = sorted(glob(os.path.join(CONDA_DIR, 'etc', 'jupyterhub', 'jupyterhub_config.d', '*.py')))
for ec in extra_configs:
    load_subconfig(ec)