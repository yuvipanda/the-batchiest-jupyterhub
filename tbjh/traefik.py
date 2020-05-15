"""Traefik installation and setup"""
import hashlib
import os
import json
import pathlib

from jinja2 import Template
from passlib.apache import HtpasswdFile

