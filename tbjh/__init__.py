import sys
import os
import pathlib
from jupyterhub_traefik_proxy.install import install_traefik

HERE = pathlib.Path(__file__).absolute().parent
CONDA_DIR = pathlib.Path(os.environ['CONDA_DIR'])
CONFIG_DIR = CONDA_DIR / "etc/jupyterhub"


def install_unit(name: str, unit: str, systemd_unit_path='/etc/systemd/system/'):
    """
    Install systemd unit with name & contents unit
    """
    with open(os.path.join(systemd_unit_path, f'{name}.service'), 'w') as f:
        f.write(unit)

def main():
    # Traefik binary should be installed
    install_traefik(CONDA_DIR / 'bin', f'{sys.platform}-amd64', '1.7.18')
    # All our config should be here
    os.makedirs(CONFIG_DIR, exist_ok=True)
    # Subdirectory where we look for config items is created
    os.makedirs(CONFIG_DIR / 'jupyterhub_config.d', exist_ok=True)

    # Subdirectory with db, state files
    os.makedirs(CONDA_DIR / 'var/jupyterhub', exist_ok=True)

    with open(HERE / 'systemd-units/jupyterhub.service') as f:
        hub_unit = f.read().format(
            install_prefix=str(CONDA_DIR),
            jupyterhub_config_path=str(HERE / 'jupyterhub_config.py')
        )
        install_unit('jupyterhub', hub_unit)


if __name__ == '__main__':
    main()