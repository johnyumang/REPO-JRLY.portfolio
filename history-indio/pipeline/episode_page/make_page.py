#!/usr/bin/env python3
"""Build a private download page for one History Indio episode.

usage: make_page.py <episode_dir> <full_quality.mp4> <out_dir> [--part-mb 14]

Writes <out_dir>/page.html, <out_dir>/files.json, <out_dir>/media/preview.mp4 and
<out_dir>/media/<name>_pNN.mp4 (raw byte parts, named .mp4 only because artifacts serve a fixed list of file types; a part is not playable on its own; of the full MP4, each at most 14 MB, because a
published Artifact file may be at most 15 MB). The page joins the parts in the browser and saves
one MP4. Keep <out_dir> OUTSIDE the repo (scratchpad): audio and video are never committed.
"""
import argparse, hashlib, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BOARD = "https://claude.ai/artifact/QiKdeQGV7tMTt2DJTVwPVC"
MB = 1024 * 1024
PREVIEW_LIMIT = 15 * MB
PART_EXT = ".mp4"   # artifacts refuse unknown extensions and application/octet-stream; .mp4 is a served type


def episode_info(ep_dir):
    name = os.path.basename(os.path.normpath(ep_dir))
    m = re.match(r"ep0*(\d+)", name)
    if not m:
        sys.exit(f"cannot read the episode number from folder name {name!r} (expected epNN-slug)")
    n = int(m.group(1))
    cap_path = None
    for f in ("captions_trending.md", "captions.md"):
        p = os.path.join(ep_dir, f)
        if os.path.exists(p):
            cap_path = p
            break
    if not cap_path:
        sys.exit("no captions_trending.md or captions.md in " + ep_dir)
    text = open(cap_path, encoding="utf-8").read()
    head = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), "")
    m = re.search(r"Episode\s+\d+\s*:\s*(.+)$", head)
    title = (m.group(1) if m else name.split("-", 1)[-1].replace("-", " ").title()).strip()
    return n, title, cap_path, text


def parse_blocks(text):
    """Split the captions file into [{h, text}] by its '## ' headings (intro before the first heading is dropped)."""
    blocks, cur = [], None
    for line in text.splitlines():
        if line.startswith("## "):
            if cur:
                blocks.append(cur)
            cur = {"h": line[3:].strip(), "lines": []}
        elif cur is not None:
            cur["lines"].append(line)
    if cur:
        blocks.append(cur)
    out = []
    for b in blocks:
        t = "\n".join(b["lines"]).strip()
        if t:
            out.append({"h": b["h"], "text": t})
    return out


def safe_name(n, title):
    t = re.sub(r"\([^)]*\)", "", title)
    t = re.sub(r"[^A-Za-z0-9]+", "_", t.replace("ñ", "n").replace("Ñ", "N")).strip("_")
    return f"HistoryIndio_EP{n}_{t}" if t else f"HistoryIndio_EP{n}"


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def make_preview(src, dst):
    dur = max(duration(src), 1.0)
    audio_k = 80
    # aim for about 13.5 MB so the 15 MB limit is not hit; never above 600 kbps video
    video_k = int(min(600, 13.5 * MB * 8 / 1000 / dur - audio_k - 10))
    for _ in range(6):
        video_k = max(video_k, 120)
        cmd = ["nice", "-n", "10", "ffmpeg", "-v", "error", "-y", "-i", src,
               "-vf", "scale=540:960:force_original_aspect_ratio=decrease,pad=540:960:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
               "-c:v", "libx264", "-preset", "veryfast", "-threads", "2",
               "-b:v", f"{video_k}k", "-maxrate", f"{int(video_k * 1.2)}k", "-bufsize", f"{video_k * 2}k",
               "-c:a", "aac", "-b:a", f"{audio_k}k", "-ac", "2", "-movflags", "+faststart", dst]
        subprocess.run(cmd, check=True)
        size = os.path.getsize(dst)
        print(f"preview: {video_k} kbps video + {audio_k} kbps audio -> {size / MB:.2f} MB")
        if size < PREVIEW_LIMIT:
            return size
        video_k = int(video_k * 0.75)
    sys.exit("preview is still over 15 MB after retries")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(MB), b""):
            h.update(chunk)
    return h.hexdigest()


def split_file(src, media_dir, base, part_bytes):
    """Write raw byte parts; return their paths. Verifies the join with sha256."""
    paths, i = [], 1
    with open(src, "rb") as f:
        while True:
            data = f.read(part_bytes)
            if not data:
                break
            p = os.path.join(media_dir, f"{base}_p{i:02d}{PART_EXT}")
            with open(p, "wb") as o:
                o.write(data)
            paths.append(p)
            i += 1
    h = hashlib.sha256()
    for p in paths:
        with open(p, "rb") as f:
            h.update(f.read())
    want = sha256(src)
    if h.hexdigest() != want:
        sys.exit("joined parts do not match the original file (sha256)")
    print(f"parts: {len(paths)} x <= {part_bytes / MB:.2f} MB; joined sha256 matches {want[:16]}…")
    return paths


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode_dir")
    ap.add_argument("full_mp4")
    ap.add_argument("out_dir")
    ap.add_argument("--part-mb", type=float, default=14.0, help="part size in MB (max 14; smaller only for tests)")
    a = ap.parse_args()
    if a.part_mb > 14:
        sys.exit("--part-mb must be 14 or less (15 MB per published file)")
    repo = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    out = os.path.abspath(a.out_dir)
    if out.startswith(repo + os.sep):
        print("WARNING: out_dir is inside the repo; video must never be committed. Prefer the scratchpad.")
    media = os.path.join(out, "media")
    os.makedirs(media, exist_ok=True)

    n, title, cap_path, text = episode_info(a.episode_dir)
    blocks = parse_blocks(text)
    base = safe_name(n, title)
    print(f"episode {n}: {title} (captions from {os.path.basename(cap_path)}, {len(blocks)} blocks)")

    prev = os.path.join(media, "preview.mp4")
    make_preview(a.full_mp4, prev)
    parts = split_file(a.full_mp4, media, base, int(a.part_mb * MB))
    full_size = os.path.getsize(a.full_mp4)

    page = {
        "n": n, "title": title, "filename": base + ".mp4", "size": full_size,
        "preview": "media/preview.mp4",
        "parts": ["media/" + os.path.basename(p) for p in parts],
        "captions": blocks, "caption_filename": base + "_captions.txt", "board": BOARD,
    }
    tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    data = json.dumps(page, ensure_ascii=False).replace("</", "<\\/")
    html = tpl.replace("__TITLE__", f"History Indio EP {n}").replace("/*__PAGE_DATA__*/null", data)
    with open(os.path.join(out, "page.html"), "w", encoding="utf-8") as f:
        f.write(html)

    files = {"media/preview.mp4": prev}
    for p in parts:
        files["media/" + os.path.basename(p)] = p
    with open(os.path.join(out, "files.json"), "w", encoding="utf-8") as f:
        json.dump(files, f, indent=1, ensure_ascii=False)

    desc = f"Episode {n}: {title} — panoorin ang preview at i-download ang full-quality MP4 at captions."
    print("\nPUBLISH (Artifact tool, private, do not pass url for a new page):")
    print(json.dumps({"file_path": os.path.join(out, "page.html"), "title": f"History Indio EP {n}",
                      "description": desc, "icon": "video", "capabilities": {"downloads": True},
                      "files": files}, indent=1, ensure_ascii=False))
    print(f"\nfull MP4: {full_size / MB:.2f} MB in {len(parts)} parts; files map also saved in {os.path.join(out, 'files.json')}")


if __name__ == "__main__":
    main()
