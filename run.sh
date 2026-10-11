#!/bin/bash
# homeexchangeradar launcher: pulls the latest code from GitHub, then runs it.
#
# secrets.json (your real API keys/cookie) stays local, is gitignored, and is
# never touched by the pull. This is the single command to point Synology
# Task Scheduler (or cron, or a systemd timer) at.
#
# Usage: bash run.sh   (run from anywhere; it cd's into its own directory)

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

if [ ! -d .git ]; then
  echo "run.sh must live inside the homeexchangeradar git checkout (no .git found in $REPO_DIR)." >&2
  echo "Clone it first: git clone https://github.com/gerardcm/homeexchangeradar.git" >&2
  exit 1
fi

echo "Pulling latest code..."
git pull --ff-only

if [ ! -f secrets.json ]; then
  echo "secrets.json not found in $REPO_DIR." >&2
  echo "Copy secrets.example.json to secrets.json and fill in your real values first." >&2
  exit 1
fi

echo "Running homeexchangeradar..."
python3 homeexchangeradar.py
