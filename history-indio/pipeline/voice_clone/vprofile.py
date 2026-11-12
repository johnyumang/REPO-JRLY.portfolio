"""Paths and the voice profile, shared by every voice_clone script. Nothing here is specific to one machine.
  HI_VOICE_REC      the user's own Episode 1 recording (never in the repo)            required by baseline/gen/assemble
  HI_VOICE_WORK     work root (default /opt/work/voice); baseline files in <work>/baseline
  HI_VOICE_PROFILE  voice profile (default voice_profile.json beside this file)"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.environ.get('HI_VOICE_WORK', '/opt/work/voice')
BASE = os.path.join(WORK, 'baseline')
REAL_JSON = os.path.join(BASE, 'real_ep1.json')
CENTROID = os.path.join(BASE, 'real_centroid.npy')
PROFILE = json.load(open(os.environ.get('HI_VOICE_PROFILE', os.path.join(HERE, 'voice_profile.json'))))
def rec():
    r = os.environ.get('HI_VOICE_REC', '')
    if not r or not os.path.exists(r): sys.exit('HI_VOICE_REC must point to the real Episode 1 recording (got %r)' % r)
    return r
def need(path):
    if not os.path.exists(path): sys.exit('missing %s: run baseline.py first (see README.md)' % path)
    return path
def real(): return json.load(open(need(REAL_JSON)))
def centroid():
    import numpy as np
    return np.load(need(CENTROID))
