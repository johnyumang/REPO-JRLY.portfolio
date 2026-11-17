"""Write the starting animation manifest for an episode: one shot per still, one motion prompt per shot.

usage: python3 motion.py <episode dir, e.g. videos/ep01b-1min> <out manifest.json>
         [--stills DIR]       use DIR/<still>.jpg (16:9 stills from stills.py) when present, else <ep>/full/<still>.jpg
         [--image-base URL]   write image URLs as URL/<still>.jpg instead of local paths (for the studio)
         [--shots 0-1]        keep only these shots (index range or comma list)
         [--audio voice.wav]  file name of the voice in the render's public dir

Reads key_prompts.json (which still each line uses + what is in it), shots_fx.json (the move and its reason),
timings.json (when each line is spoken) and script_multispeaker.txt (the picture note above each line).

Motion rules written into every prompt:
  1. keep the art style of the still (animate the painting, never restyle it);
  2. one continuous shot: no camera cuts, no scene change inside a clip;
  3. only the motion the line needs (a shout moves; a narrated line breathes);
  4. faces stay on model (same features, no morphing);
  5. no hands-only shots (a still whose subject is just hands is flagged for a redraw).
"""
import json, os, re, sys

STYLE_LOCK = ("Animate this exact painting: keep the same hand-painted anime look, the same ink lines, colours and light; "
              "nothing is restyled or redrawn.")
ONE_SHOT = "One continuous shot from start to end: no cuts, no scene change, no new people appear."
FACE_LOCK = ("Every face stays on model: same features, same eyes, same hair, no morphing. Hands stay natural with five "
             "fingers; the camera never moves onto the hands alone.")
NEGATIVE = ("camera cut, scene change, transition, morphing face, face change, extra fingers, extra limbs, duplicate person, "
            "hands only, close-up of hands, text, subtitles, watermark, blurry, low quality, photorealistic, 3d render, restyled")

CAMERA = {
    "hold": "The camera holds still with only a faint drift.",
    "push_in": "The camera pushes in slowly and slightly.",
    "dolly_in": "The camera moves forward toward the subject, steady and firm.",
    "pull_out": "The camera pulls back slowly.",
    "crane_down": "The camera descends slowly from above.",
    "crane_up": "The camera rises slowly.",
    "tilt_up": "The camera tilts up slowly and stops on the top of the frame.",
    "tilt_down": "The camera tilts down slowly.",
    "pan_left": "The camera pans slowly to the left.",
    "pan_right": "The camera pans slowly to the right.",
    "orbit_left": "The camera circles slowly to the left around the subject.",
    "orbit_right": "The camera circles slowly to the right around the subject.",
    "rack_focus": "The camera holds still while the focus shifts.",
}
ACTION = {
    "shout": "{who} shouts, mouth opening wide, a sharp lean forward; the rest of the body stays steady.",
    "dramatic": "{who} reacts with wide eyes and a small tremble.",
    "playful": "{who} tilts the head with a lively small movement.",
    "whisper": "{who} speaks softly, lips barely moving.",
    "quiet": "{who} speaks quietly, lips moving gently.",
    "hard": "{who} speaks firmly, jaw set, a small nod.",
    "cold": "{who} speaks coldly, almost still.",
    "dry": "{who} gives a tired small sigh.",
    "awed": "{who} looks up in wonder, eyes shining.",
    "curious": "{who} raises the eyebrows slightly, lips moving.",
}
CALM = "Only small natural movement: breathing, a blink, hair and cloth stirring."
FX = {"embers": "Embers drift up through the air.", "water": "Rain falls.", "sparkle": "A soft glow pulses.",
      "smoke": "Smoke drifts.", "dust": "Dust floats in the light."}
HANDS_ONLY = re.compile(r"(close[- ]up|detail)\s+(shot\s+)?of\s+(his|her|their|a|the)?\s*(two\s+)?(hand|hands|fingers|wrists?|palm)\b", re.I)
NARRATORS = {"TAGAPAGSALAYSAY", "NARRATOR"}


def picture_notes(script_path, n):
    """The (picture note) above each spoken line, in order; '' where there is none."""
    notes, pending = [], ""
    if not os.path.exists(script_path):
        return [""] * n
    for raw in open(script_path, encoding="utf-8"):
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("(") and s.endswith(")"):
            pending = s[1:-1].strip()
        elif re.match(r"^[A-Z][A-Z ]+(\([^)]*\))?:", s):
            notes.append(pending)
            pending = ""
    return (notes + [""] * n)[:n]


def parse_range(spec, n):
    out = set()
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out.update(range(int(a), int(b) + 1))
        elif part:
            out.add(int(part))
    return [i for i in sorted(out) if i < n]


def build(ep, stills_dir=None, image_base=None, audio="voice.wav"):
    kp = json.load(open(os.path.join(ep, "key_prompts.json"), encoding="utf-8"))
    fx_all = json.load(open(os.path.join(ep, "shots_fx.json"), encoding="utf-8")) if os.path.exists(os.path.join(ep, "shots_fx.json")) else {}
    lines = json.load(open(os.path.join(ep, "timings.json"), encoding="utf-8"))
    notes = picture_notes(os.path.join(ep, "script_multispeaker.txt"), len(lines))
    shots_map, full = kp.get("shots", {}), kp.get("full", {})

    def still_of(i, prev):
        fx = fx_all.get(str(i), {})
        if "key" in fx and str(fx["key"]) in shots_map:
            return shots_map[str(fx["key"])]["full"]
        if str(i) in shots_map:
            return shots_map[str(i)]["full"]
        return prev

    groups, prev = [], None
    for i, _ in enumerate(lines):
        st = still_of(i, prev)
        if groups and st == groups[-1]["still"]:
            groups[-1]["lines"].append(i)
        else:
            groups.append({"still": st, "lines": [i]})
        prev = st

    shots = []
    for g_i, g in enumerate(groups):
        first, last = lines[g["lines"][0]], lines[g["lines"][-1]]
        start = 0.0 if g_i == 0 else round((lines[g["lines"][0] - 1]["end"] + first["start"]) / 2, 3)
        if g_i + 1 < len(groups):
            nxt = lines[groups[g_i + 1]["lines"][0]]
            end = round((last["end"] + nxt["start"]) / 2, 3)
        else:
            end = round(last["end"] + 0.8, 3)
        fx = fx_all.get(str(g["lines"][0]), {})
        info = full.get(g["still"], {})
        subject = info.get("subject", "")
        main = lines[g["lines"][0]]
        style = next((lines[i].get("style") for i in g["lines"] if lines[i].get("style") == "shout"), main.get("style", "calm"))
        speaker = next((lines[i]["speaker"] for i in g["lines"] if lines[i].get("speaker") not in NARRATORS), None)
        who = (speaker or "the person").title() if speaker else "The person"
        action = ACTION.get(style, CALM).format(who=who) if speaker else CALM
        move = fx.get("move", "hold") if fx.get("why") else "hold"   # no reason, no move (CAMERA.md rule 1)
        parts = [STYLE_LOCK, ONE_SHOT, CAMERA.get(move, CAMERA["hold"]), action]
        parts += [FX[f] for f in fx.get("fx", []) if f in FX]
        note = notes[g["lines"][0]]
        if note:
            parts.append("The picture: " + note.rstrip(".") + ".")
        parts.append(FACE_LOCK)
        length = round(end - start, 3)
        img_name = g["still"] + ".jpg"
        if image_base:
            image = image_base.rstrip("/") + "/" + img_name
        elif stills_dir and os.path.exists(os.path.join(stills_dir, img_name)):
            image = os.path.abspath(os.path.join(stills_dir, img_name))
        else:
            image = os.path.abspath(os.path.join(ep, "full", img_name))
        shot = {
            "id": "s%02d" % g_i, "still": g["still"], "image": image,
            "prompt": " ".join(parts), "negative": NEGATIVE,
            "duration": round(min(5.0, max(1.5, length + 0.25)), 2),
            "start": start, "end": end, "lines": g["lines"],
            "move": move, "why": fx.get("why", ""),
            "shout": any(lines[i].get("style") == "shout" for i in g["lines"]),
            "trans_in": "fade" if fx.get("trans_in") in ("fade", "dissolve") else "cut",   # never a cross-dissolve
            "caption": "bottom", "provider": "wan-free", "takes": [], "clip": None,
        }
        if HANDS_ONLY.search(subject):
            shot["warning"] = "hands-only still: redraw with a face in frame before animating"
        shots.append(shot)

    return {
        "version": 1, "episode": os.path.basename(os.path.normpath(ep)), "fps": 30, "width": 1920, "height": 1080,
        "audio": audio,
        "lines": [{"i": i, "text": l["text"], "speaker": l.get("speaker", ""), "style": l.get("style", ""),
                   "start": l["start"], "end": l["end"]} for i, l in enumerate(lines)],
        "shots": shots,
    }


def main(a):
    if len(a) < 2:
        sys.exit(__doc__)
    opt = lambda f: a[a.index(f) + 1] if f in a else None
    m = build(a[0], opt("--stills"), opt("--image-base"), opt("--audio") or "voice.wav")
    if opt("--shots"):
        keep = parse_range(opt("--shots"), len(m["shots"]))
        m["shots"] = [m["shots"][i] for i in keep]
        used = {i for s in m["shots"] for i in s["lines"]}
        m["lines"] = [l for l in m["lines"] if l["i"] in used]
    os.makedirs(os.path.dirname(os.path.abspath(a[1])), exist_ok=True)
    json.dump(m, open(a[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for s in m["shots"]:
        print(f'{s["id"]} {s["still"]} {s["start"]:6.2f}-{s["end"]:6.2f}s move={s["move"]}' + (f'  WARNING: {s["warning"]}' if "warning" in s else ""))
    print("manifest:", a[1], len(m["shots"]), "shots")


if __name__ == "__main__":
    main(sys.argv[1:])
