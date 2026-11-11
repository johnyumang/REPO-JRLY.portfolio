#!/usr/bin/env python3
"""Pull a clean narrator sample out of a finished video that has music under the voice.
usage: prep_reference.py video.mp4 narrator.wav   (needs ffmpeg and the `demucs` package; model weights from Hugging Face)"""
import os, subprocess, sys, tempfile
src, out = sys.argv[1:3]; tmp = tempfile.mkdtemp()
wav = os.path.join(tmp, 'a.wav'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vn', '-ac', '2', '-ar', '44100', wav], check=True)
cmd = [sys.executable, '-m', 'demucs', '-n', 'htdemucs_ft', '--two-stems', 'vocals', '-o', tmp, wav]
if os.environ.get('DEMUCS_REPO'): cmd[3:3] = ['--repo', os.environ['DEMUCS_REPO']]      # local folder holding the htdemucs_ft weights
subprocess.run(cmd, check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(tmp, 'htdemucs_ft', 'a', 'vocals.wav'), '-af',
                'silenceremove=stop_periods=-1:stop_duration=0.35:stop_threshold=-38dB', '-ac', '1', '-ar', '24000', '-t', '22', out], check=True)
print('wrote', out)
