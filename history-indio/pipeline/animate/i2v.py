"""Run a manifest's shots through image-to-video and save the clips in a work dir (outside the repo).

usage: python3 i2v.py <manifest.json> <work dir> [--provider wan-free|comfy|minimax] [--force] [--tries N]

  wan-free  the free Hugging Face Space (gradio client). Optional env HF_TOKEN gives more free GPU quota.
  comfy     Wan 2.2 on your own NVIDIA card through a local ComfyUI (free, no daily limit; see comfy() below).
  minimax   MiniMax image-to-video (spends credits). Env MINIMAX_API_KEY (may be left unset on a machine whose
            proxy adds it), MINIMAX_API_HOST (default https://api.minimax.io), MINIMAX_MODEL (default in code).

Each shot gets <work>/clips/<id>.mp4; the manifest is updated in place with "clip" (path relative to the work dir),
"clip_duration" and a "takes" entry. Shots that already have a clip on disk are skipped unless --force; a clip given as a URL (a take picked in the
studio) is downloaded instead of generated.
"""
import base64, json, mimetypes, os, shutil, subprocess, sys, time, urllib.parse, urllib.request

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


# ---------- comfy (Wan 2.2 on your own GPU through a local ComfyUI; free, no daily limit) ----------
# Needs ComfyUI running (default http://127.0.0.1:8188, env COMFY_URL) with the Wan 2.2 14B image-to-video files in its
# models folders. File names can be changed with env vars; defaults are the names ComfyUI's own Wan 2.2 template uses:
#   diffusion_models/ COMFY_HIGH (wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors), COMFY_LOW (..._low_noise_...)
#   loras/            COMFY_LORA_HIGH / COMFY_LORA_LOW (lightx2v 4-step LoRAs; set to "" to run without them, 20 steps)
#   text_encoders/    COMFY_CLIP (umt5_xxl_fp8_e4m3fn_scaled.safetensors)      vae/ COMFY_VAE (wan_2.1_vae.safetensors)
# COMFY_GGUF=1 loads the two models with the ComfyUI-GGUF node (UnetLoaderGGUF) instead, for cards with 10-12 GB.
COMFY_URL = os.environ.get("COMFY_URL", "http://127.0.0.1:8188").rstrip("/")


def _env(k, d):
    return os.environ.get(k, d)


def comfy_workflow(img_name, prompt, negative, frames, seed, w=832, h=480):
    gguf = _env("COMFY_GGUF", "") == "1"
    lora_h = _env("COMFY_LORA_HIGH", "wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors")
    lora_l = _env("COMFY_LORA_LOW", "wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors")
    fast = bool(lora_h and lora_l)
    steps, cfg, split = (4, 1.0, 2) if fast else (20, 3.5, 10)
    loader = (lambda n: {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": n}}) if gguf else \
             (lambda n: {"class_type": "UNETLoader", "inputs": {"unet_name": n, "weight_dtype": "default"}})
    wf = {
        "1": loader(_env("COMFY_HIGH", "wan2.2_i2v_high_noise_14B_Q4_K_M.gguf" if gguf else "wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors")),
        "2": loader(_env("COMFY_LOW", "wan2.2_i2v_low_noise_14B_Q4_K_M.gguf" if gguf else "wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors")),
        "5": {"class_type": "CLIPLoader", "inputs": {"clip_name": _env("COMFY_CLIP", "umt5_xxl_fp8_e4m3fn_scaled.safetensors"), "type": "wan"}},
        "6": {"class_type": "VAELoader", "inputs": {"vae_name": _env("COMFY_VAE", "wan_2.1_vae.safetensors")}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["5", 0]}},
        "8": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["5", 0]}},
        "9": {"class_type": "LoadImage", "inputs": {"image": img_name}},
        "10": {"class_type": "WanImageToVideo", "inputs": {"positive": ["7", 0], "negative": ["8", 0], "vae": ["6", 0],
               "start_image": ["9", 0], "width": w, "height": h, "length": frames, "batch_size": 1}},
    }
    mh, ml = ["1", 0], ["2", 0]
    if fast:
        wf["3"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": mh, "lora_name": lora_h, "strength_model": 1.0}}
        wf["4"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ml, "lora_name": lora_l, "strength_model": 1.0}}
        mh, ml = ["3", 0], ["4", 0]
    wf["11"] = {"class_type": "ModelSamplingSD3", "inputs": {"model": mh, "shift": 5.0}}
    wf["12"] = {"class_type": "ModelSamplingSD3", "inputs": {"model": ml, "shift": 5.0}}
    common = {"cfg": cfg, "sampler_name": "euler", "scheduler": "simple", "steps": steps, "noise_seed": seed,
              "positive": ["10", 0], "negative": ["10", 1]}
    wf["13"] = {"class_type": "KSamplerAdvanced", "inputs": {**common, "model": ["11", 0], "add_noise": "enable",
                "latent_image": ["10", 2], "start_at_step": 0, "end_at_step": split, "return_with_leftover_noise": "enable"}}
    wf["14"] = {"class_type": "KSamplerAdvanced", "inputs": {**common, "model": ["12", 0], "add_noise": "disable",
                "latent_image": ["13", 0], "start_at_step": split, "end_at_step": 10000, "return_with_leftover_noise": "disable"}}
    wf["15"] = {"class_type": "VAEDecode", "inputs": {"samples": ["14", 0], "vae": ["6", 0]}}
    wf["16"] = {"class_type": "CreateVideo", "inputs": {"images": ["15", 0], "fps": 16}}
    wf["17"] = {"class_type": "SaveVideo", "inputs": {"video": ["16", 0], "filename_prefix": "indio/clip", "format": "mp4", "codec": "h264"}}
    return wf


def _comfy(path, body=None, raw=None, ctype=None):
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(COMFY_URL + path, data=data, method="POST" if data is not None else "GET",
                                 headers={"Content-Type": ctype or "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        b = r.read()
    return json.loads(b) if b[:1] in (b"{", b"[") else b


def comfy(shot, img, out):
    import random, uuid
    boundary = uuid.uuid4().hex
    name = os.path.basename(img)
    raw = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{name}\"\r\n"
           f"Content-Type: image/jpeg\r\n\r\n").encode() + open(img, "rb").read() + \
          (f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n").encode()
    up = _comfy("/upload/image", raw=raw, ctype=f"multipart/form-data; boundary={boundary}")
    dur = max(1.0, min(5.0, float(shot.get("duration", 3.5))))
    frames = int(round(dur * 16 / 4)) * 4 + 1          # Wan wants 4n+1 frames at 16 fps
    seed = random.randint(1, 2**31 - 1)
    wf = comfy_workflow(up["name"], shot["prompt"], shot.get("negative", ""), frames, seed)
    pid = _comfy("/prompt", {"prompt": wf})["prompt_id"]
    print(f"  comfy job {pid} ({frames} frames)", flush=True)
    for _ in range(720):                                # up to an hour per clip
        time.sleep(5)
        h = _comfy(f"/history/{pid}")
        if pid not in h:
            continue
        st = h[pid].get("status", {})
        if st.get("status_str") == "error":
            raise RuntimeError("comfy error: " + json.dumps(st.get("messages", []))[:400])
        for o in h[pid].get("outputs", {}).values():
            for k in ("images", "videos", "gifs"):
                for f in o.get(k, []):
                    if f.get("filename", "").endswith((".mp4", ".webm")):
                        q = urllib.parse.urlencode({"filename": f["filename"], "subfolder": f.get("subfolder", ""), "type": f.get("type", "output")})
                        open(out, "wb").write(_comfy("/view?" + q))
                        return {"provider": "comfy", "seed": seed}
    raise TimeoutError("comfy job still running after an hour")


PROVIDERS = {"wan-free": wan_free, "minimax": minimax, "comfy": comfy}


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
