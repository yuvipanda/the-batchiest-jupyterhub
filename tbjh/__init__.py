import sys
import os
import pathlib
from jupyterhub_traefik_proxy.install import install_traefik

HERE = os.path.dirname(os.path.abspath(__file__))
CONDA_DIR = pathlib.Path(os.environ['CONDA_DIR'])

def main():
    install_traefik(CONDA_DIR / 'bin', f'{sys.platform}-amd64', '1.7.18')

if __name__ == '__main__':
    main()