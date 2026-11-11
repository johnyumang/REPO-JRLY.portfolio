#!/usr/bin/env bash
# One-time setup for the Blender proof shot (CPU only, no GPU needed).
set -euo pipefail
W=${1:-/opt/bl}
mkdir -p "$W/model"
python3 -m venv "$W/v"
"$W/v/bin/pip" install -q bpy numpy pillow          # bpy 5.3.0 ships a Python 3.13 wheel
# bpy needs GL/Vulkan libraries present even for Cycles; Mesa's software drivers are enough
apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
  libegl1 libgl1 libgl1-mesa-dri libglx-mesa0 libvulkan1 mesa-vulkan-drivers libxkbcommon0 libsm6 libxi6 libxxf86vm1 libxfixes3 libxrender1
# Rigged character: VRoid sample "HairSample_Male" (licence embedded in the file's VRM meta: CC0).
# Not committed to this repo; fetched from https://github.com/madjin/vrm-samples
curl -sSL -o "$W/model/host.glb" https://raw.githubusercontent.com/madjin/vrm-samples/master/vroid/beta/HairSample_Male.vrm
echo "ready: $W/v/bin/python host_shot.py --model $W/model/host.glb --out $W/out/frames"
