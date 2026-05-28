#!/usr/bin/env bash

set -euo pipefail

REPO_DIR="/opt/mcdc/codhem"
BRANCH="main"

cd "$REPO_DIR"

git fetch origin "$BRANCH"
git reset --hard "origin/$BRANCH"
uv sync --locked
