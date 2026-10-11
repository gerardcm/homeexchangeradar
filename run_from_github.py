#!/usr/bin/env python3
"""
run_from_github.py

Fetches the latest homeexchangeradar.py straight from GitHub (raw file, no
git required on the host) and runs it. Same pattern as movieradar's launcher
of the same name -- here it's the code itself that's fetched fresh each run
instead of a local checkout being updated.

secrets.json (your real API keys/cookie) lives locally next to this
launcher and is never fetched from GitHub -- only homeexchangeradar.py is.
searches.json is unaffected either way: homeexchangeradar.py already fetches
that live from GitHub itself at runtime via secrets.json's configuration_url.

Point Task Scheduler / cron at:
    python3 /path/to/run_from_github.py
"""

import os
import subprocess
import sys
import urllib.request

RAW_URL = "https://raw.githubusercontent.com/gerardcm/homeexchangeradar/main/homeexchangeradar.py"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FETCHED_SCRIPT = os.path.join(SCRIPT_DIR, "_homeexchangeradar_fetched.py")
SECRETS_PATH = os.path.join(SCRIPT_DIR, "secrets.json")


def fetch_latest():
    req = urllib.request.Request(RAW_URL, headers={"User-Agent": "homeexchangeradar-launcher"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        code = resp.read()
    if not code.strip():
        sys.exit(f"Fetched empty file from {RAW_URL} -- aborting rather than running nothing.")
    with open(FETCHED_SCRIPT, "wb") as f:
        f.write(code)


def main():
    if not os.path.exists(SECRETS_PATH):
        sys.exit(
            f"secrets.json not found at {SECRETS_PATH}.\n"
            "Copy secrets.example.json to secrets.json in this same folder and "
            "fill in your real values first."
        )

    print(f"Fetching latest homeexchangeradar.py from {RAW_URL} ...")
    fetch_latest()

    print("Running homeexchangeradar...")
    # The fetched script finds secrets.json next to itself (same SCRIPT_DIR
    # logic as homeexchangeradar.py), so no extra arguments are needed here.
    result = subprocess.run([sys.executable, FETCHED_SCRIPT])
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
