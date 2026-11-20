#!/usr/bin/env python3
"""Photoreal key stills for the SIIL teaser on the free FLUX endpoint (NVIDIA catalog).
usage: still.py OUT_DIR [shot ...]     shots: reach, pull, hold, hold12   (two takes each; the endpoint picks its own seed)"""
import json, sys, os, base64, urllib.request, urllib.error, time
BASE = ("Real photograph, shot on a phone lying at the bottom of a deep brown kraft paper bag with the lens pointing straight up. "
        "The crumpled brown paper walls of the bag surround the picture on all four sides, close to the lens and out of focus, "
        "warm daylight glowing through the paper. In the middle of the frame is the open top of the bag: a rectangular opening with a paper rim, "
        "and through it a clear blue sky. The camera is inside the bag; the person is outside the bag, standing over it. "
        "Natural daylight, true-to-life skin texture, photorealistic, sharp focus on the hands, no face visible. Vertical 9:16.")
OUTSIDE = ("The arm is outside the bag: the forearm and sleeve are seen only through the opening, against the blue sky, coming over the paper rim from beyond it. "
           "No arm, sleeve or hand comes out of the paper walls or from the edge of the picture in front of the paper.")
HAND = "a woman's hand with two thin gold rings and short natural nails, wearing a dark navy coat sleeve,"
POUCH = ("a rectangular frosted translucent matte plastic zip pouch with a slider zip along its top edge, packed completely full: "
         "a folded black fabric belt fills the whole pouch from edge to edge and corner to corner, pressed flat against the plastic, "
         "so the pouch is one flat, even, solid charcoal-black rectangle behind the frosted plastic, with no slit, no hole, "
         "no light gap and no lighter stripe anywhere, especially not in the middle")
SHOTS = {
    "reach": f"{BASE} {HAND[0].upper() + HAND[1:]} reaches over the rim of the bag from outside and down through the opening, the open hand just entering the bag, fingers relaxed, pointing down towards the camera. {OUTSIDE} Each hand has exactly five fingers.",
    "pull": f"{BASE} {HAND[0].upper() + HAND[1:]} holds the top corner of {POUCH}, lifting the pouch up out of the bag towards the sky. Each hand has exactly five fingers.",
    "hold": (f"{BASE} Two hands of a woman with thin gold rings and dark navy sleeves hold up {POUCH}. The pouch is held flat and upright, "
             "facing the camera, above the bag and outside it, seen through the opening against the blue sky. Both arms are outside the bag: the wrists and sleeves are seen only through the opening, against the sky, coming over the paper rim from beyond it, never out of the paper walls. Both hands are outside the pouch: one hand pinches the top edge "
             "from above and the other hand pinches the bottom edge from below, fingertips and thumbs resting on the outer surface of the plastic. "
             "No hand or finger is inside the pouch or behind the frosted plastic. "
             "Printed on the front of the pouch in clean white serif capital letters, centred: the word \"SIIL\" and, smaller, directly under it, the word \"OSTOMY\". "
             "No other writing. Each hand has exactly five fingers."),
    "hold12": (f"{BASE} One arm of a woman in a dark navy sleeve comes straight down from the top of the picture, from twelve o'clock, "
               f"over the top rim of the bag, and her hand, with a thin gold ring, holds up {POUCH}. The pouch hangs upright, tall and "
               "vertical, facing the camera, in the middle of the opening against the blue sky; her fingers pinch the middle of its top edge "
               "from above, fingertips on the outer surface of the plastic. Only this one hand; no hand at the bottom or at the sides; "
               "nothing comes in from the left or the right. The arm is outside the bag, seen only through the opening, against the sky. "
               "Printed on the front of the pouch in clean white serif capital letters, centred: the word \"SIIL\" and, smaller, directly under it, "
               "the word \"OSTOMY\". No other writing. The hand has exactly five fingers."),
}
NEG = ("cartoon, illustration, anime, drawing, painting, 3d render, cgi, plastic skin, extra fingers, six fingers, missing fingers, fused fingers, "
       "deformed hands, extra hands, extra arms, face, watermark, logo, caption, subtitles, border, frame, black bars, blurry, low quality")
def call(body, out):
    req = urllib.request.Request("https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux-3-image-klein", data=json.dumps(body).encode(),
                                 headers={"Accept": "application/json", "Content-Type": "application/json", "NVCF-POLL-SECONDS": "60",
                                          **({"Authorization": "Bearer " + os.environ["NVIDIA_API_KEY"]} if os.environ.get("NVIDIA_API_KEY") else {})})
    try: r = json.load(urllib.request.urlopen(req, timeout=180))
    except urllib.error.HTTPError as e: print('HTTP', e.code, e.read()[:200].decode('utf-8', 'replace')); return False
    except Exception as e: print('ERR', e); return False
    a = r.get('artifacts') or []
    if not a or not a[0].get('base64'): print('EMPTY', (a[0].get('finishReason') if a else str(r)[:200])); return False
    open(out, 'wb').write(base64.b64decode(a[0]['base64'])); return True
if __name__ == '__main__':
    out_dir = sys.argv[1]; os.makedirs(out_dir, exist_ok=True)
    for shot in (sys.argv[2:] or list(SHOTS)):
        for seed in (int(s) for s in os.environ.get('SEEDS', '11,23').split(',')):
            out = f"{out_dir}/{shot}_{seed}.jpg"
            for t in range(5):
                t0 = time.time()
                if call(dict(prompt=SHOTS[shot], negative_prompt=NEG, width=768, height=1344, steps=30, cfg_scale=4.0), out):   # the endpoint no longer takes a seed
                    print('ok %.0fs' % (time.time() - t0), out, flush=True); break
                time.sleep(6 + 6 * t)
