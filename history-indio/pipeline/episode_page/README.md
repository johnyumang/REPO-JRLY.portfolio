# Episode download page
Builds one private Artifact page per episode: a preview player, a button to download the full-quality MP4, and each caption block from `captions_trending.md` (or `captions.md`) with a copy button.
Command: `python3 pipeline/episode_page/make_page.py videos/<slug> <full_quality.mp4> <scratchpad>/ep_page_<slug>` (needs ffmpeg). It prints the publish call.
Publish with the Artifact tool: private, `file_path` = `<out_dir>/page.html`, `capabilities` `{"downloads": true}`, and `files` = the map in `<out_dir>/files.json` (also printed).
A published file may be at most 15 MB, so the full MP4 is split into raw byte parts of 14 MB or less, named `_pNN.mp4` because artifacts only serve a fixed list of file types (a part is not playable on its own). The page joins them in the browser and saves one MP4 (checked with sha256 when the parts are made).
Never commit audio or video: keep `<out_dir>` in the scratchpad, outside the repo.
