"""Traefik installation and setup"""
import hashlib
import os
from urllib.request import urlretrieve

from jinja2 import Template

from tljh.configurer import load_config

# FIXME: support more than one platform here
plat = "linux-amd64"
traefik_version = "1.6.5"

# record sha256 hashes for supported platforms here
checksums = {
    "linux-amd64": "9e77c7664e316953e3f5463c323dffeeecbb35d0b1db7fb49f52e1d9464ca193"
}


def checksum_file(path):
    """Compute the sha256 checksum of a path"""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def ensure_traefik_binary(prefix):
    """Download and install the traefik binary"""
    traefik_bin = os.path.join(prefix, "bin", "traefik")
    if os.path.exists(traefik_bin):
        checksum = checksum_file(traefik_bin)
        if checksum == checksums[plat]:
            # already have the right binary
            # ensure permissions and we're done
            os.chmod(traefik_bin, 0o755)
            return
        else:
            print(f"checksum mismatch on {traefik_bin}")
            os.remove(traefik_bin)

    traefik_url = (
        "https://github.com/containous/traefik/releases"
        f"/download/v{traefik_version}/traefik_{plat}"
    )
    print(f"Downloading traefik {traefik_version}...")
    # download the file
    urlretrieve(traefik_url, traefik_bin)
    os.chmod(traefik_bin, 0o755)

    # verify that we got what we expected
    checksum = checksum_file(traefik_bin)
    if checksum != checksums[plat]:
        raise IOError(f"Checksum failed {traefik_bin}: {checksum} != {checksums[plat]}")


def ensure_traefik_config(state_dir):
    """Render the traefik.toml config file"""
    config = load_config()
    with open(os.path.join(os.path.dirname(__file__), "traefik.toml.tpl")) as f:
        template = Template(f.read())
    new_toml = template.render(config)
    https = config["https"]
    letsencrypt = https["letsencrypt"]
    tls = https["tls"]
    # validate https config
    if https["enabled"]:
        if not tls["cert"] and not letsencrypt["email"]:
            raise ValueError(
                "To enable https, you must set tls.cert+key or letsencrypt.email+domains"
            )
        if (letsencrypt["email"] and not letsencrypt["domains"]) or (
            letsencrypt["domains"] and not letsencrypt["email"]
        ):
            raise ValueError("Both email and domains must be set for letsencrypt")
    with open(os.path.join(state_dir, "traefik.toml"), "w") as f:
        os.fchmod(f.fileno(), 0o744)
        f.write(new_toml)

    # ensure acme.json exists and is private
    with open(os.path.join(state_dir, "acme.json"), "a") as f:
        os.fchmod(f.fileno(), 0o600)

