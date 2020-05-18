import sys
import os
import pathlib
import json
import secrets
from jupyterhub_traefik_proxy.install import install_traefik
from passlib.apache import HtpasswdFile
from jinja2 import Template
from urllib.request import urlretrieve
from tbjh import constants


def ensure_traefik_credentials(path: pathlib.Path):
    """
    Ensure we have persistent username / password creds for traefik.

    We want this to be as stable as possible, and not change each
    time this script is run. So we write it to a separate file with
    a version string, and re-generate it only if that version changes.
    """
    current_version = 'v1'

    if path.exists():
        with open(path) as f:
            creds = json.load(f)

        if 'version' not in creds:
            # uh, valid JSON file that's from someone else?
            raise ValueError(f'Unrecognized traefik credentials file in {path}')

        if creds['version'] == current_version:
            # We don't need to do anything
            return

    with open(path, 'w') as f:
        creds = {
            'version': current_version,
            'username': secrets.token_hex(32),
            'password': secrets.token_hex(32)
        }
        json.dump(creds, f, indent=4)
        os.fchmod(f.fileno(), 0o600)


def ensure_traefik_config(creds_path: pathlib.Path, config_path: pathlib.Path, state_dir: pathlib.Path):
    """
    Render the traefik.toml config file
    """
    with open(creds_path) as f:
        creds = json.load(f)
        # generate htpassword that works with traefik
        ht = HtpasswdFile()
        ht.set_password(creds['username'], creds['password'])
        hashed_password = str(ht.to_string()).split(":")[1][:-3]
        basic_auth = f'{creds["username"]}:{hashed_password}'

    config = {
        'traefik_api': {
            'basic_auth': basic_auth,
            'port': 8099,
            'ip': '127.0.0.1'
        },
        'http': {
            'port': 8181
        },
        'https': {
            'port': 443,
            'enabled': False
        }
    }

    with open(HERE / "traefik.toml.tpl") as f:
        template = Template(f.read())

    new_toml = template.render(config)

    with open(config_path, 'w') as f:
        os.fchmod(f.fileno(), 0o600)
        f.write(new_toml)

    with open(state_dir / "rules.toml", "w") as f:
        os.fchmod(f.fileno(), 0o600)

    # ensure acme.json exists and is private
    with open(state_dir / "acme.json", "a") as f:
        os.fchmod(f.fileno(), 0o600)


def install_unit(name: str, unit: str, systemd_unit_path='/etc/systemd/system'):
    """
    Install systemd unit with name & contents unit
    """
    with open(os.path.join(systemd_unit_path, f'{name}.service'), 'w') as f:
        f.write(unit)


def main():
    # Traefik binary should be installed
    install_traefik(constants.BIN_DIR, f'{sys.platform}-amd64', '1.7.18')

    # All our config should be here
    os.makedirs(constants.CONFIG_DIR, exist_ok=True)
    # Subdirectory where we look for config items is created
    os.makedirs(constants.JUPYTERHUB_CONFIG_D_DIR, exist_ok=True)

    # Subdirectory with db, state files
    os.makedirs(constants.STATE_DIR, exist_ok=True)


    with open(HERE / 'systemd-units/jupyterhub.service') as f:
        hub_unit = f.read().format(
            install_prefix=str(CONDA_DIR),
            jupyterhub_config_path=str(HERE / 'jupyterhub_config.py')
        )
        install_unit('jupyterhub', hub_unit)

    ensure_traefik_credentials(constants.TRAEFIK_CREDS_PATH)

    ensure_traefik_config(
        constants.TRAEFIK_CREDS_PATH,
        constants.CONFIG_DIR / "traefik.toml",
        constants.STATE_DIR
    )

    with open(HERE / 'systemd-units/traefik.service') as f:
        traefik_unit = f.read().format(
            install_prefix=str(CONDA_DIR),
        )
        install_unit('traefik', traefik_unit)

    # Download miniforge installer into a place `jupyterhub_config.py` can find
    # FIXME: Retry this download
    # FIXME: Validate SHA of download, so we don't have to re-download
    urlretrieve(constants.MINIFORGE_URL, constants.MINIFORGE_INSTALLER_PATH)


if __name__ == '__main__':
    main()