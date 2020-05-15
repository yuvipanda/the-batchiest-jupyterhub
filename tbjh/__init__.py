import sys
import os
import pathlib
from jupyterhub_traefik_proxy.install import install_traefik

HERE = os.path.dirname(os.path.abspath(__file__))
CONDA_DIR = pathlib.Path(os.environ['CONDA_DIR'])

def main():
    # Traefik binary should be installed
    install_traefik(CONDA_DIR / 'bin', f'{sys.platform}-amd64', '1.7.18')
    # Subdirectory where we look for config items is created
    os.makedirs(CONDA_DIR / 'etc/jupyterhub_config.d', exist_ok=True)

if __name__ == '__main__':
    main()