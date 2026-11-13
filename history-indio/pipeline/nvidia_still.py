import json, sys, base64, urllib.request, time
def call(model, body, out, poll=25):
    req = urllib.request.Request(f"https://ai.api.nvidia.com/v1/genai/{model}", data=json.dumps(body).encode(),
                                 headers={"Accept": "application/json", "Content-Type": "application/json", "NVCF-POLL-SECONDS": str(poll)})
    t = time.time()
    try: r = json.load(urllib.request.urlopen(req, timeout=120))
    except urllib.error.HTTPError as e: print(model, 'HTTP', e.code, e.read()[:300].decode('utf-8', 'replace')); return False
    a = r.get('artifacts') or r.get('data') or []
    b64 = (a[0].get('base64') or a[0].get('b64_json')) if a else r.get('image')
    if not b64:                                                          # usually the content filter (finishReason CONTENT_FILTERED): reword the prompt plainly
        print(model, 'EMPTY: no picture came back,', (a[0].get('finishReason') if a else None) or 'no reason given'); return False
    data = base64.b64decode(b64)                                         # decode first: a reply with no image must not empty an existing file
    open(out, 'wb').write(data); print(model, 'ok %.0fs' % (time.time() - t), out, a[0].get('finishReason', '') if a else ''); return True
if __name__ == '__main__':
    P = ("Vertical anime key frame, modern dark-fantasy shonen action anime style, bold confident ink line art, sharp cel shading with hard-edged shadows, dramatic lighting, rich saturated colour, cinematic composition. "
         "A young pre-colonial Visayan warrior in his late teens, warm brown skin, messy black hair with a red headband tied at the back, gold disc earrings, blue-black geometric tattoos on arms and chest, open sleeveless dark indigo vest with gold trim, red waist sash over loose black trousers, raises a kampilan sword on a beach at night under a full moon, waves crashing behind him, nipa huts with torches in the distance. No text.")
    for m, extra in (("black-forest-labs/flux-3-image-klein", {}), ("black-forest-labs/flux.2-klein-4b", {})):
        ok = call(m, {"prompt": P, "width": 768, "height": 1344, "seed": 7, **extra}, f"t_{m.split('/')[1]}.jpg")
        if not ok: call(m, {"prompt": P, "seed": 7}, f"t_{m.split('/')[1]}.jpg")
