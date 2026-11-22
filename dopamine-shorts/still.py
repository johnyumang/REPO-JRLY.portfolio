"""Photoreal 9:16 still on the free NVIDIA endpoint. usage: still.py <out.jpg> "<scene>" [seed]"""
import json, sys, base64, urllib.request, time
LOOK = ("Photorealistic vertical 9:16 frame from a high-end action sports film or commercial, shot on a cinema camera, "
        "natural lighting, realistic textures, sharp focus, shallow depth of field where fitting, rich but natural colour grade, high dynamic range. ")
TAIL = " No text, no letters, no logos, no brand names, no watermark, no signage anywhere in the frame."
NEG = ("text, letters, words, numbers, logo, brand, watermark, signature, caption, sign, label, sticker, "
       "cartoon, anime, illustration, painting, 3d render, cgi look, plastic, oversaturated, "
       "deformed hands, extra fingers, extra limbs, distorted face, duplicate, blurry, low detail, collage, border, frame")
def make(out, scene, seed=11, tries=4):
    body = dict(prompt=(LOOK + scene + TAIL)[:1990], negative_prompt=NEG, width=768, height=1344, seed=seed, steps=30, cfg_scale=4.0)
    for t in range(tries):
        body['seed'] = seed + t
        req = urllib.request.Request("https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux-3-image-klein", data=json.dumps(body).encode(),
              headers={"Accept": "application/json", "Content-Type": "application/json", "NVCF-POLL-SECONDS": "60"})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=180)); a = r.get('artifacts') or []
            if a and a[0].get('base64'): open(out, 'wb').write(base64.b64decode(a[0]['base64'])); print('ok', out, flush=True); return True
            print('EMPTY', a[0].get('finishReason') if a else r)
        except urllib.error.HTTPError as e: print('HTTP', e.code, e.read()[:200])
        except Exception as e: print('ERR', e)
        time.sleep(4 + 4 * t)
    return False
if __name__ == '__main__': make(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 11)
