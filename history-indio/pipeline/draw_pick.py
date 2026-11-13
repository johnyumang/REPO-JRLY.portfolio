#!/usr/bin/env python3
"""Draw several candidates of ONE still on the full-quality free model and put them on one sheet, to choose from.
For a still that has failed its redraws: many draws and a strict choice beat one more try (audit/README.md, "The many-draws way").
usage (from history-indio/):  draw_pick.py <out_dir> <prompt.txt> <seed,seed,...> ["<negative prompt, at most 500 characters>"]
writes <out_dir>/c<seed>.jpg (768x1344) and <out_dir>/sheet.jpg (all candidates side by side, small).
The prompt is sent as written (up to 2000 characters; nothing is replaced or cut): start it with the episode's style line,
end it with "Vertical 9:16. No text, no letters, no logos, no watermarks." flux-3, 30 steps, guidance 4. The service refuses
the word "seven" and some clothing words ("faded sage-green"): reword and go on. Keep <out_dir> outside the repository."""
import sys, os, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import flux_hq
from PIL import Image, ImageDraw
NEG = ("text, letters, watermark, logo, comic panels, border, extra fingers, six fingers, fused fingers, deformed hands, extra limbs, extra arms, "
       "extra legs, five legs, three hind legs, extra paws, two tails, two dogs, duplicate person, twin, distorted face, crossed eyes, blurry, photo, 3d render")
if __name__ == '__main__':
    if len(sys.argv) < 4: sys.exit(__doc__)
    out_dir, P = sys.argv[1], open(sys.argv[2], encoding='utf-8').read().strip(); seeds = [int(x) for x in sys.argv[3].split(',')]
    neg = sys.argv[4] if len(sys.argv) > 4 else NEG; os.makedirs(out_dir, exist_ok=True)
    if len(P) > 2000: sys.exit('the prompt has %d characters; the model takes 2000' % len(P))
    if len(neg) > 500: sys.exit('the negative prompt has %d characters; the model takes 500' % len(neg))
    print('prompt', len(P), 'characters; negative', len(neg), flush=True)
    def one(seed):
        return seed, flux_hq.call(dict(prompt=P, negative_prompt=neg, width=768, height=1344, seed=seed, steps=30, cfg_scale=4.0), '%s/c%d.jpg' % (out_dir, seed))
    with cf.ThreadPoolExecutor(3) as ex:
        for s, ok in ex.map(one, seeds): print(s, ok, flush=True)
    ims = []
    for s in seeds:
        p = '%s/c%d.jpg' % (out_dir, s)
        if os.path.exists(p):
            im = Image.open(p).convert('RGB').resize((384, 672)); d = ImageDraw.Draw(im); d.rectangle([0, 0, 64, 20], fill=(0, 0, 0)); d.text((4, 4), 'seed %d' % s, fill=(255, 255, 0)); ims.append(im)
    if ims:
        sh = Image.new('RGB', (384 * len(ims), 672)); [sh.paste(im, (i * 384, 0)) for i, im in enumerate(ims)]; sh.save(out_dir + '/sheet.jpg', quality=86); print('sheet', out_dir + '/sheet.jpg', sh.size)
