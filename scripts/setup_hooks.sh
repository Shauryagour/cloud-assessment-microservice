#!/usr/bin/env bash
# Sets up Git hooks to automatically block pushes if tests fail.

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "Configuring Git hooks in: $REPO_ROOT"

# Ensure hook is executable
chmod +x .githooks/pre-push

# Configure git to use .githooks directory
git config core.hooksPath .githooks

echo "Git pre-push hook installed successfully!"
echo "Pushes will now be automatically rejected if pytest fails."
