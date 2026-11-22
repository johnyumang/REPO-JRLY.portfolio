"""Paths and the voice profile, shared by every voice_clone script. Nothing here is specific to one machine.
  HI_VOICE_REC      the user's own Episode 1 recording (never in the repo)            required by baseline/gen/assemble
  HI_VOICE_WORK     work root (default /opt/work/voice); baseline files in <work>/baseline
  HI_VOICE_PROFILE  voice profile (default voice_profile.json beside this file)
  Season 2 cast references: <work>/cast/<NAME>.wav + <NAME>.txt (never in the repo)"""
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
# Season 2 cast (designed voices): private reference clip + its exact transcript per character
CAST = os.path.join(WORK, 'cast')                      # <NAME>.wav + <NAME>.txt (NAME with spaces as underscores)
CASTWORK = os.path.join(WORK, 'castwork')              # design candidates and their checks
NARRATOR = 'INDIO'                                     # the one voice cloned from the user's own recording
def fname(name): return name.strip().upper().replace(' ', '_')
def cast_ref(name):
    w = os.path.join(CAST, fname(name) + '.wav'); t = w[:-4] + '.txt'
    if not (os.path.exists(w) and os.path.exists(t)): sys.exit('missing cast reference %s (+ .txt) for %s' % (w, name))
    return w, open(t).read().strip()
