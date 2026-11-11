#!/usr/bin/env bash
# One-time setup per machine/session. Safe to re-run. Needs: python3, node 22+, ffmpeg, Playwright with Chromium.
set -e
HI="$(cd "$(dirname "$0")/.." && pwd)"
[ -x /opt/vc/bin/python ] || python3 -m venv /opt/vc
/opt/vc/bin/pip install -q --upgrade pip
/opt/vc/bin/pip install -q torch torchaudio "transformers==4.46.3" numpy pillow soundfile librosa scipy
[ -x /opt/cb/bin/python ] || python3 -m venv /opt/cb
/opt/cb/bin/pip install -q --upgrade pip
/opt/cb/bin/pip install -q chatterbox-tts "setuptools<81"
cd "$HI/engine3d" && npm i --silent && ln -sfn "$(npm root -g)/playwright" node_modules/playwright
echo "setup ok"
