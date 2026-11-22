#!/usr/bin/env bash
# Optional, once per machine, after pipeline/setup.sh: the voice-clone stack. Downloads about 5 GB (VoxCPM2 4.7 GB; the
# check models, Whisper large-v3-turbo, MMS aligner and WavLM, download on first use); generation needs about 11 GB RAM.
# - /opt/vc gets faster-whisper (the Tagalog listener used by the checks)
# - VoxCPM2 in its own venv /opt/vx layered on /opt/vc (reuses its torch), so /opt/vc is untouched
# - /opt/vx_model32: the VoxCPM2 snapshot (symlinks) with config dtype float32 instead of bfloat16, for CPU
set -e
[ -x /opt/vc/bin/python ] || { echo "run pipeline/setup.sh first"; exit 1; }
/opt/vc/bin/pip install -q --no-cache-dir faster-whisper==1.2.1
[ -x /opt/vx/bin/python ] || python3 -m venv /opt/vx
SP=$(/opt/vx/bin/python -c "import site;print(site.getsitepackages()[0])")
echo "$(/opt/vc/bin/python -c 'import site;print(site.getsitepackages()[0])')" > "$SP/zz_vc_layer.pth"
/opt/vx/bin/pip install -q --upgrade pip
/opt/vx/bin/pip install -q --no-cache-dir voxcpm==2.0.3
/opt/vx/bin/python - <<'P'
import os, json
from huggingface_hub import snapshot_download
p = snapshot_download('openbmb/VoxCPM2'); print('model at', p)
d = os.environ.get('HI_VOX_MODEL', '/opt/vx_model32'); os.makedirs(d, exist_ok=True)
for f in os.listdir(p):
    if f != 'config.json' and not os.path.lexists(os.path.join(d, f)): os.symlink(os.path.join(p, f), os.path.join(d, f))
c = json.load(open(os.path.join(p, 'config.json'))); c['dtype'] = 'float32'; json.dump(c, open(os.path.join(d, 'config.json'), 'w'), indent=2)
print('float32 copy at', d)
P
echo "vox setup ok"
