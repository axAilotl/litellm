#!/bin/bash

set -euo pipefail

# print current dir 
echo
pwd


# only run this step for litellm enterprise, we run this if enterprise/enterprise_ui/_enterprise.json exists
if [ ! -f "enterprise/enterprise_ui/enterprise_colors.json" ]; then
    echo "Admin UI - using default LiteLLM UI"
    exit 0
fi

echo "Building Custom Admin UI..."

# Reuse the selected image/developer runtime; never install a separate nvm Node.
bash "$(dirname -- "${BASH_SOURCE[0]}")/check_node_runtime.sh"

# copy _enterprise.json from this directory to /ui/litellm-dashboard, and rename it to ui_colors.json
cp enterprise/enterprise_ui/enterprise_colors.json ui/litellm-dashboard/ui_colors.json

# cd in to /ui/litellm-dashboard
cd ui/litellm-dashboard

# ensure have access to build_ui.sh
chmod +x ./build_ui.sh

# run ./build_ui.sh
./build_ui.sh

# return to root directory
cd ../..
