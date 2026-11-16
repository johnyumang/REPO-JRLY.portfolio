# Every engine this project uses, and how to take it with you (all free)

Nothing here is paid. Three kinds: models that run on your own computer (free forever, no quota), one free picture
endpoint, and one free motion Space with a daily quota that refills by itself. When a quota is used up, wait.

| What it makes | Engine | Where it runs | Cost and limit | What you need | Script |
|---|---|---|---|---|---|
| Stills (the Bakunawa look) | FLUX `flux-3-image-klein` on NVIDIA's API catalog | NVIDIA's servers | free tier; rate-limited (429/502 when busy: wait and retry, one request at a time) | free key from build.nvidia.com in `NVIDIA_API_KEY` | `pipeline/flux_hq.py`, `pipeline/draw_pick.py`, `pipeline/nvidia_still.py` |
| Real motion clips (3.5 s) | Wan 2.2 image-to-video Space | Hugging Face ZeroGPU | free daily quota, about 6 clips a day per account; refills the next day | free Hugging Face token in `HF_TOKEN` | `pipeline/wan_clip.py` |
| Voices: Indio clone and designed cast | VoxCPM2 (`openbmb/VoxCPM2`, Apache-2.0) | your computer, CPU | free, no limit; 1-2 min per sentence | the owner's own recording for Indio; 16 GB RAM | `pipeline/voice_clone/` |
| Checking the voices (words heard) | faster-whisper `deepdml/faster-whisper-large-v3-turbo-ct2` | your computer | free | - | `pipeline/voice_clone/vqc.py` |
| Checking the voices (same speaker) | WavLM `microsoft/wavlm-base-plus-sv` | your computer | free | - | `pipeline/voice_clone/vqc.py` |
| Word timing | MMS aligner `MahmoudAshraf/mms-300m-1130-forced-aligner`; `openai/whisper-small` | your computer | free | - | `pipeline/voice_clone/vqc.py`, `pipeline/align_audio.py` |
| Fallback Tagalog voice (no clone) | MMS-TTS `facebook/mms-tts-tgl` | your computer | free | - | `pipeline/tts_mms.py` |
| Depth for the 3D camera | `depth-anything/Depth-Anything-V2-Small-hf` | your computer | free | - | `pipeline/build_anime.py`, `pipeline/depth3d.py` |
| Camera moves, effects, subtitles, final video | our own code + ffmpeg + OpenCV | your computer | free | ffmpeg | `pipeline/build_anime.py`, `pipeline/subtitles.py` |
| Music bed and sound effects | made in code (no samples, no service) | your computer | free | - | `pipeline/soundtrack.py`, `pipeline/sound_design.py` |
| Writing on signs, baybayin | our own code + open fonts | your computer | free | - | `pipeline/sign_text.py`, `pipeline/baybayin.py` |
| Backup photos (rarely used) | Unsplash API | Unsplash | free tier, 50 requests an hour | free Access Key in `UNSPLASH_ACCESS_KEY` | `pipeline/unsplash_backup.py` |

The models that run on your computer download themselves from Hugging Face the first time (about 11 GB in all).
`bash pipeline/setup.sh` and `bash pipeline/voice_clone/setup_vox.sh` install everything.

## Keys: three, all free, all in the environment only
```
export NVIDIA_API_KEY=...        # build.nvidia.com -> any model page -> "Get API key"
export HF_TOKEN=...              # huggingface.co -> Settings -> Access Tokens -> read
export UNSPLASH_ACCESS_KEY=...   # optional
```
Never put a key in a file of this repository or in a chat. On the cloud machines the keys were added by the
environment itself, which is why the scripts also work there without these variables.

## Not used, on purpose
ElevenLabs, Figma, Canva and any other paid or credit-based generator. If a script ever asks for one, that is a bug.
