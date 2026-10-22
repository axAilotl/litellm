#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
expected_node_version="$(tr -d '[:space:]' < "${project_root}/.node-version")"
if ! command -v node >/dev/null || ! command -v npm >/dev/null; then
    echo "Error: install Node.js ${expected_node_version} and npm before building the Admin UI." >&2
    exit 1
fi
actual_node_version="$(node -p 'process.versions.node')"
if [[ "${actual_node_version}" != "${expected_node_version}" ]]; then
    echo "Error: Admin UI requires Node.js ${expected_node_version}; found ${actual_node_version}." >&2
    exit 1
fi
npm --version >/dev/null
