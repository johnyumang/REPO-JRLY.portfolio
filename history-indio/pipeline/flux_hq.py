"""FLUX stills at the Bakunawa look: one markdown-structured prompt + a negative prompt, on flux-3-image-klein (free NVIDIA endpoint).
usage: flux_hq.py <out.jpg> <subject> <setting> <light> [--seed N] [--steps N] [--cfg X] [--tries N]"""
import json, sys, base64, urllib.request, time
STYLE = """# STYLE
Hand-painted anime key visual for a dark-fantasy shonen series. Bold confident ink line art, sharp cel shading with hard-edged shadows, rich saturated colour, dramatic rim light, deep painterly background full of detail, cinematic depth, film-poster finish. One single moment, one picture."""
RULES = """# ANATOMY
Correct human anatomy. Each hand has exactly five fingers, natural pose, clean fingernails. Symmetrical eyes, clean faces. One of each named character.
# FRAME
Vertical 9:16. The picture fills the whole frame, edge to edge. No text anywhere."""
NEG = ("text, letters, words, numbers, captions, subtitles, signature, watermark, logo, user interface, speech bubble, "
       "comic panels, collage, split screen, border, frame, black bars, "
       "extra fingers, six fingers, missing fingers, fused fingers, deformed hands, extra limbs, extra arms, duplicate person, twin, "
       "distorted face, crossed eyes, melted face, blurry, low detail, flat colours, 3d render, photo, plastic skin, "
       "japanese signage, chinese characters, torii, cherry blossom")
def prompt(subject, setting, light): return f"{STYLE}\n# SUBJECT\n{subject}\n# SETTING\n{setting}\n# LIGHT AND MOOD\n{light}\n{RULES}"
def call(body, out, model="black-forest-labs/flux-3-image-klein"):
    req = urllib.request.Request(f"https://ai.api.nvidia.com/v1/genai/{model}", data=json.dumps(body).encode(), headers={"Accept": "application/json", "Content-Type": "application/json", "NVCF-POLL-SECONDS": "60"})
    try: r = json.load(urllib.request.urlopen(req, timeout=180))
    except urllib.error.HTTPError as e: print('HTTP', e.code, e.read()[:300].decode('utf-8', 'replace')); return False
    except Exception as e: print('ERR', e); return False
    a = r.get('artifacts') or []
    if not a or not a[0].get('base64'): print('EMPTY', (a[0].get('finishReason') if a else r)); return False   # usually the content filter: reword
    open(out, 'wb').write(base64.b64decode(a[0]['base64'])); return True
def make(out, subject, setting, light, seed=7, steps=30, cfg=4.0, tries=4, w=768, h=1344):
    body = dict(prompt=prompt(subject, setting, light), negative_prompt=NEG, width=w, height=h, seed=seed, steps=steps, cfg_scale=cfg)
    for t in range(tries):
        t0 = time.time()
        body['seed'] = seed + t
        if call(body, out): print('ok %.0fs' % (time.time() - t0), out, flush=True); return True
        time.sleep(4 + 4 * t)
    return False
if __name__ == '__main__':
    a = sys.argv[1:]; g = lambda f, d: type(d)(a[a.index(f) + 1]) if f in a else d
    make(a[0], a[1], a[2], a[3], seed=g('--seed', 7), steps=g('--steps', 30), cfg=g('--cfg', 4.0), tries=g('--tries', 4))
