#!/usr/bin/env bash
# AI Platform Apps - initial setup
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

echo "=== AI Platform Apps Setup ==="

# Check Python
python3 --version || { echo "Python 3 required"; exit 1; }

# Install CLI
echo "Installing app-manager CLI..."
pip install -e app-manager/ 2>/dev/null || pip install --break-system-packages -e app-manager/

echo "Done! Run: deploy --help"
