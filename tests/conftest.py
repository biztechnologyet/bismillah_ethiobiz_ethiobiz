"""Bismillah — shared test helpers for the EthioBiz full system suite."""
import os
import sys

# Repository roots so unit tests can import app modules without install.
WORKSPACE = r"C:\BISMALLAH ETHIOBIZ.ET CLOUD SYSTEMS INSHA'ALLAH"
REPOS = {
    "bizmarketing": os.path.join(WORKSPACE, "bizmarketing"),
    "bismillah_ethiobiz": os.path.join(WORKSPACE, "bismillah_ethiobiz_ethiobiz"),
}


def ensure_repo_on_path(*repos):
    for r in repos:
        path = REPOS.get(r, r)
        if path not in sys.path:
            sys.path.insert(0, path)


SERVER_HOST = "128.140.82.215"
SERVER_USER = "root"
CONTAINER_BACKEND = "bismallah_ethiobiz_inshaallah-backend-1"
SITE = "ethiobiz.et"
