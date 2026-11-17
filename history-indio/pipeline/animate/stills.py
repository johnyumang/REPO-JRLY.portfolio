"""Make the 16:9 stills a manifest needs (the episode stills are drawn 9:16 for the vertical cut).

usage: python3 stills.py <episode dir> <manifest.json> <out dir> [--no-draw]

For each still in the manifest: if <out dir>/<still>.jpg exists it is kept. Otherwise it is redrawn wide from the same
key prompt (subject, setting, light) with the free draw service in ../flux_hq.py (request body without a "seed" field),
asking for every face in the upper two thirds so the captions never cover one. If drawing fails (or --no-draw), the
9:16 still is centred on a blurred, darkened copy of itself so nothing is cropped. The manifest's image paths are
then pointed at the 16:9 files.
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import flux_hq  # noqa: E402

WIDE = ("Horizontal 16:9 widescreen. Every face in the upper two thirds of the frame; the bottom quarter is background "
        "only (captions go there).")


def fit_blur(src, dst, w=1344, h=768):
    from PIL import Image, ImageFilter, ImageEnhance
    im = Image.open(src).convert("RGB")
    bg = im.resize((w, int(im.height * w / im.width))).crop((0, 0, w, h))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(28))).enhance(0.45)
    fg = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
    bg.paste(fg, ((w - fg.width) // 2, 0))
    bg.save(dst, quality=92)


def draw_wide(info, out, tries=3):
    p = flux_hq.prompt(info["subject"], info.get("setting", ""), info.get("light", "")).replace("Vertical 9:16.", WIDE)
    body = dict(prompt=p, negative_prompt=flux_hq.NEG, width=1344, height=768, steps=30, cfg_scale=4.0)   # no "seed"
    for t in range(tries):
        if flux_hq.call(body, out):
            return True
        time.sleep(5 + 5 * t)
    return False


def main(a):
    if len(a) < 3:
        sys.exit(__doc__)
    ep, man_path, out_dir = a[0], a[1], a[2]
    os.makedirs(out_dir, exist_ok=True)
    full = json.load(open(os.path.join(ep, "key_prompts.json"), encoding="utf-8")).get("full", {})
    m = json.load(open(man_path, encoding="utf-8"))
    for s in m["shots"]:
        out = os.path.join(out_dir, s["still"] + ".jpg")
        if not os.path.exists(out):
            ok = "--no-draw" not in a and s["still"] in full and draw_wide(full[s["still"]], out)
            if ok:
                print("drew 16:9", out, flush=True)
            else:
                fit_blur(os.path.join(ep, "full", s["still"] + ".jpg"), out)
                print("fitted 9:16 on blur", out, flush=True)
        s["image"] = os.path.abspath(out)
    json.dump(m, open(man_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
