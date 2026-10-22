#!/bin/bash

set -euo pipefail

# Direct UI builds use the same project-owned runtime as Docker builds.
bash "$(dirname -- "${BASH_SOURCE[0]}")/../../docker/check_node_runtime.sh"

# print contents of ui_colors.json
echo "Contents of ui_colors.json:"
cat ui_colors.json

# Install the locked UI dependencies with the selected runtime.
npm ci

# Run npm build
npm run build

# Check if the build was successful
if [ $? -eq 0 ]; then
  echo "Build successful. Copying files..."

  # echo current dir
  echo
  pwd

  # Specify the destination directory
  destination_dir="../../litellm/proxy/_experimental/out"

  # Remove existing files in the destination directory
  rm -rf "$destination_dir"/*

  # Copy the contents of the output directory to the specified destination
  cp -r ./out/* "$destination_dir"

  rm -rf ./out

  echo "Deployment completed."
else
  echo "Build failed. Deployment aborted."
fi
