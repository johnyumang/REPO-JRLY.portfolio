# ebook/ — build tooling for the INDIO novel

Only tooling lives here. The manuscript, the detailed story, covers, EPUB/PDF files, audio and video are
**never** committed (this repository is public). They are kept in a private folder and delivered as private pages.

| File | What it does |
|---|---|
| `build_book.py` | `python3 build_book.py <manuscript_dir> <out_dir> [--no-pdf] [--epubcheck <python>]` builds the cover (1600×2560 ebook, 1800×2700 print), EPUB 3 (pandoc) and a 6×9 in PDF (pandoc HTML + Playwright Chromium). |
| `book.example.json` | Book definition; a chapter entry may also be `{"part": "title"}` to start a new part, so one volume can hold all five books. Missing chapter art is skipped with a warning. |
| (old) `book.example.json` | Book definition: title, chapters and which episode frame illustrates each. Copy it into the private manuscript folder as `book.json`. |
| `epub.css`, `print.css` | Ebook and print styles (Tala ng Saksi box, scene breaks, chapter art). |
| `pdf.cjs` | HTML → 6×9 in PDF with page numbers. |
| `make_trailer.py` | `python3 make_trailer.py <out_dir> [--size 720] [--cover cover.jpg]`: a 29-second book trailer (9:16 and 1:1) and a 6-second cover loop from existing frames, with the synthesized music bed of `pipeline/soundtrack.py`. |

Needs: pandoc, Pillow, numpy, soundfile, ffmpeg, node with Playwright. EPUB validation: `pip install epubcheck`, then
`python -m epubcheck book.epub` (needs Java).

Rules: no sales claims that are not true; "Kathang-isip sina Indio at Usman; totoo ang kasaysayan" on the cover and in the
front matter; every chapter ends with its Tala ng Saksi (tiyak, pinagtatalunan, kathang-isip).
