"""Run a manifest's shots through image-to-video and save the clips in a work dir (outside the repo).

usage: python3 i2v.py <manifest.json> <work dir> [--provider wan-free|minimax] [--force] [--tries N]

  wan-free  the free Hugging Face Space (gradio client). Optional env HF_TOKEN gives more free GPU quota.
  minimax   MiniMax image-to-video (spends credits). Env MINIMAX_API_KEY (may be left unset on a machine whose
            proxy adds it), MINIMAX_API_HOST (default https://api.minimax.io), MINIMAX_MODEL (default in code).

Each shot gets <work>/clips/<id>.mp4; the manifest is updated in place with "clip" (path relative to the work dir),
"clip_duration" and a "takes" entry. Shots that already have a clip on disk are skipped unless --force; a clip given as a URL (a take picked in the
studio) is downloaded instead of generated.
"""
import base64, json, mimetypes, os, shutil, subprocess, sys, time, urllib.request

WAN_SPACE = "https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space"
MINIMAX_HOST = os.environ.get("MINIMAX_API_HOST", "https://api.minimax.io").rstrip("/")
MINIMAX_MODEL = os.environ.get("MINIMAX_MODEL", "MiniMax-Hailuo-02")


def probe_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    try:
        return round(float(r.stdout.strip()), 3)
    except ValueError:
        return None


def local_image(src, work):
    """A local path for the shot's image (downloads a URL into the work dir)."""
    if src.startswith(("http://", "https://")):
        os.makedirs(os.path.join(work, "images"), exist_ok=True)
        dst = os.path.join(work, "images", os.path.basename(src.split("?")[0]) or "image.jpg")
        if not os.path.exists(dst):
            urllib.request.urlretrieve(src, dst)
        return dst
    return src


# ---------- wan-free (gradio) ----------
_client = None


def wan_client():
    global _client
    if _client is None:
        from gradio_client import Client
        tok = os.environ.get("HF_TOKEN")
        try:
            _client = Client(WAN_SPACE, token=tok) if tok else Client(WAN_SPACE)
        except TypeError:   # older gradio_client
            _client = Client(WAN_SPACE, hf_token=tok)
    return _client


def wan_free(shot, img, out):
    from gradio_client import handle_file
    dur = max(0.5, min(5.0, float(shot.get("duration", 3.5))))
    r = wan_client().predict(handle_file(img), shot["prompt"], 6, shot.get("negative", ""), dur, 1, 1, 42, True,
                             api_name="/generate_video")
    v = r[0]["video"] if isinstance(r[0], dict) else r[0]
    shutil.copy(v, out)
    return {"provider": "wan-free", "seed": r[1] if len(r) > 1 else None}


# ---------- minimax ----------
# Request/response shapes as used here: POST /v1/video_generation {model, prompt, first_frame_image, duration,
# resolution} -> {task_id, base_resp}; GET /v1/query/video_generation?task_id= -> {status, file_id};
# GET /v1/files/retrieve?file_id= -> {file: {download_url}}. Same shapes as studio/lib/providers/minimax.ts.
def _mm(path, body=None):
    h = {"Content-Type": "application/json"}
    if os.environ.get("MINIMAX_API_KEY"):
        h["Authorization"] = "Bearer " + os.environ["MINIMAX_API_KEY"]
    req = urllib.request.Request(MINIMAX_HOST + path, data=json.dumps(body).encode() if body else None, headers=h,
                                 method="POST" if body else "GET")
    r = json.load(urllib.request.urlopen(req, timeout=60))
    br = r.get("base_resp") or {}
    if br.get("status_code", 0) != 0:
        raise RuntimeError(f"minimax error {br.get('status_code')}: {br.get('status_msg')}")
    return r


def minimax(shot, img, out):
    mime = mimetypes.guess_type(img)[0] or "image/jpeg"
    data_url = f"data:{mime};base64," + base64.b64encode(open(img, "rb").read()).decode()
    dur = 10 if float(shot.get("duration", 6)) > 6 else 6
    t = _mm("/v1/video_generation", {"model": MINIMAX_MODEL, "prompt": shot["prompt"][:2000], "first_frame_image": data_url,
                                     "duration": dur, "resolution": os.environ.get("MINIMAX_RESOLUTION", "768P")})
    task = t["task_id"]
    print("  minimax task", task, flush=True)
    for _ in range(120):   # up to ~20 minutes
        time.sleep(10)
        q = _mm(f"/v1/query/video_generation?task_id={task}")
        st = q.get("status")
        if st == "Success":
            f = _mm(f"/v1/files/retrieve?file_id={q['file_id']}")
            urllib.request.urlretrieve(f["file"]["download_url"], out)
            return {"provider": "minimax", "task_id": task}
        if st == "Fail":
            raise RuntimeError("minimax task failed")
    raise TimeoutError("minimax task still running after 20 minutes")


PROVIDERS = {"wan-free": wan_free, "minimax": minimax}


def main(a):
    if len(a) < 2:
        sys.exit(__doc__)
    man_path, work = a[0], os.path.abspath(a[1])
    opt = lambda f, d: a[a.index(f) + 1] if f in a else d
    forced = opt("--provider", None)
    tries = int(opt("--tries", 6))
    os.makedirs(os.path.join(work, "clips"), exist_ok=True)
    m = json.load(open(man_path, encoding="utf-8"))
    failed = []
    for s in m["shots"]:
        out = os.path.join(work, "clips", s["id"] + ".mp4")
        if (s.get("clip") or "").startswith(("http://", "https://")) and "--force" not in a:
            try:   # a take picked in the studio: provider links expire, so keep a copy now
                urllib.request.urlretrieve(s["clip"], out)
                print(s["id"], "fetched", s["clip"][:80])
            except Exception as e:
                print(s["id"], "could not fetch the studio take, generating again:", repr(e)[:200])
        if os.path.exists(out) and "--force" not in a:
            s["clip"], s["clip_duration"] = "clips/" + s["id"] + ".mp4", probe_duration(out)
            print(s["id"], "kept", out)
            continue
        prov = forced or s.get("provider") or "wan-free"
        img = local_image(s["image"], work)
        for t in range(tries):
            try:
                t0 = time.time()
                info = PROVIDERS[prov](s, img, out)
                s["clip"], s["clip_duration"] = "clips/" + s["id"] + ".mp4", probe_duration(out)
                s.setdefault("takes", []).append({**info, "clip": s["clip"], "duration": s["clip_duration"]})
                print(s["id"], "ok", prov, "%.0fs" % (time.time() - t0), out, flush=True)
                break
            except Exception as e:   # quota, queue full, network: wait and try again
                wait = min(300, 30 * (t + 1))
                print(s["id"], "try", t, repr(e)[:300], f"- waiting {wait}s", flush=True)
                time.sleep(wait)
        else:
            failed.append(s["id"])
        json.dump(m, open(man_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if failed:
        sys.exit("no clip for: " + ", ".join(failed))


if __name__ == "__main__":
    main(sys.argv[1:])
