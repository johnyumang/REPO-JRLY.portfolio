#!/usr/bin/env python3
"""Build the INDIO ebook (EPUB 3 + 6x9 in PDF) from a PRIVATE manuscript folder.
usage: python3 build_book.py <manuscript_dir> <out_dir> [--no-pdf] [--epubcheck <python with epubcheck>]
The manuscript folder holds book.json (see book.example.json) and the chapter markdown files.
Nothing it produces belongs in this public repository: keep out_dir outside it.
Needs: pandoc, Pillow, node with playwright (for the PDF)."""
import json, os, re, subprocess, sys, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # history-indio/
HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
src, out = os.path.abspath(args[0]), os.path.abspath(args[1])
os.makedirs(os.path.join(out, 'img'), exist_ok=True)
B = json.load(open(os.path.join(src, 'book.json')))
FONT_DIRS = ['/usr/share/fonts', '/usr/local/share/fonts', os.path.expanduser('~/.fonts')]

def font(name, size):
    for d in FONT_DIRS:
        for root, _, files in os.walk(d):
            for f in files:
                if os.path.splitext(f)[0].lower() == os.path.splitext(name)[0].lower() and f.lower().endswith(('.ttf', '.otf')):
                    return ImageFont.truetype(os.path.join(root, f), size)
    return ImageFont.load_default()

def cover_fit(im, W, H):
    k = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))

def make_cover(path, W=1600, H=2560):
    fr = Image.open(os.path.join(HI, B['cover_frame'])).convert('RGB')
    k = W / fr.width; fr = fr.resize((W, round(fr.height * k)), Image.LANCZOS)
    top = round(H * 0.17)                                     # push the picture down so the title never covers a face
    im = cover_fit(fr, W, H).filter(ImageFilter.GaussianBlur(40))
    im.paste(fr.crop((0, 0, W, min(fr.height, H - top))), (0, top))
    fade = Image.linear_gradient('L').resize((W, 160))          # soften the seam between blur and picture
    im.paste(cover_fit(fr, W, H).filter(ImageFilter.GaussianBlur(40)).crop((0, top, W, top + 160)), (0, top), fade.transpose(Image.FLIP_TOP_BOTTOM))
    shade = Image.new('L', (W, H)); d = ImageDraw.Draw(shade)
    for y in range(H):                                        # dark at the top (title) and bottom (subtitle)
        t = y / H; a = max(0, 1 - t / 0.34) * 230 + max(0, (t - 0.70) / 0.30) * 235
        d.line([(0, y), (W, y)], fill=int(min(255, a)))
    im = Image.composite(Image.new('RGB', (W, H), (12, 8, 4)), im, shade)
    d = ImageDraw.Draw(im); gold = (240, 190, 90); cream = (250, 240, 220)
    title, sub = B['title'].split(':')[0].strip(), B['title'].split(':', 1)[1].strip() if ':' in B['title'] else ''
    f1 = font('InterDisplay-Black', 360)
    tw = d.textlength(title, font=f1); s = min(1.0, (W * 0.9) / tw); f1 = font('InterDisplay-Black', int(360 * s))
    tw = d.textlength(title, font=f1)
    d.text(((W - tw) / 2 + 8, 128), title, font=f1, fill=(0, 0, 0))
    d.text(((W - tw) / 2, 120), title, font=f1, fill=gold)
    f2 = font('InterDisplay-Bold', 110); sw = d.textlength(sub, font=f2)
    d.text(((W - sw) / 2, 120 + int(360 * s) + 40), sub, font=f2, fill=cream)
    f3 = font('InterDisplay-SemiBold', 64); st = B.get('subtitle', ''); w3 = d.textlength(st, font=f3)
    d.text(((W - w3) / 2, H - 330), st, font=f3, fill=cream)
    f4 = font('Inter-Medium', 44); tag = 'Kathang-isip sina Indio at Usman; totoo ang kasaysayan.'; w4 = d.textlength(tag, font=f4)
    d.text(((W - w4) / 2, H - 230), tag, font=f4, fill=(215, 200, 175))
    logo = os.path.join(HI, 'branding', 'history_indio_logo.png')
    if os.path.exists(logo):
        L = Image.open(logo).convert('RGBA'); L = L.resize((420, int(420 * L.height / L.width)))
        im.paste(L, ((W - L.width) // 2, H - 150), L)
    im.save(path, quality=90)

def art(rel, name, maxh=1400):
    im = Image.open(os.path.join(HI, rel)).convert('RGB')
    if im.height > maxh: im = im.resize((round(im.width * maxh / im.height), maxh), Image.LANCZOS)
    p = os.path.join(out, 'img', name); im.save(p, quality=80, optimize=True); return 'img/' + name

make_cover(os.path.join(out, 'img', 'cover.jpg'))
make_cover(os.path.join(out, 'img', 'cover_print.jpg'), 1800, 2700)
parts = []
for f in B.get('front', []):
    parts.append(open(os.path.join(src, f), encoding='utf-8').read())
parts.append(f"# {B['part_title']} {{.unnumbered .part}}\n")
for i, ch in enumerate(B['chapters'], 1):
    t = open(os.path.join(src, ch['file']), encoding='utf-8').read().strip()
    head, rest = t.split('\n', 1)
    img = art(ch['art'], f'ch{i:02d}.jpg')
    t = f"{head}\n\n![]({img}){{.chapter-art}}\n{rest}"
    t = re.sub(r'^## (Tala ng Saksi|Witness Notes)', r'## \1 {.tala}', t, flags=re.M)
    parts.append(t)
if B.get('map_frame'):
    m = art(B['map_frame'], 'map.jpg')
    parts.append(f"# Ang Kasulatan {{.unnumbered}}\n\n![]({m}){{.chapter-art}}\n\n*Labindalawang tuldok. Labindalawang medalyon. Sa Ikalawang Aklat: Ang Labindalawa.*\n")
for f in B.get('back', []):
    parts.append(open(os.path.join(src, f), encoding='utf-8').read())
md = os.path.join(out, 'book.md'); open(md, 'w', encoding='utf-8').write('\n\n'.join(parts))
meta = os.path.join(out, 'meta.yaml')
open(meta, 'w', encoding='utf-8').write(
    f"---\ntitle: \"{B['title']}\"\nsubtitle: \"{B.get('subtitle','')}\"\nauthor: \"{B['author']}\"\nlang: {B['lang']}\nrights: \"{B['rights']}\"\n"
    f"description: \"{B.get('edition','')}\"\n---\n")
shutil.copy(os.path.join(HERE, 'epub.css'), out)
base = os.path.join(out, 'indio_book')
subprocess.run(['pandoc', meta, md, '-o', base + '.epub', '--toc', '--toc-depth=1', '--split-level=1',
                '--epub-cover-image', os.path.join(out, 'img', 'cover.jpg'), '--css', os.path.join(out, 'epub.css'),
                '--resource-path', out], check=True, cwd=out)
print('EPUB', base + '.epub', os.path.getsize(base + '.epub') // 1024, 'KB')

if '--epubcheck' in args:
    py = args[args.index('--epubcheck') + 1]
    r = subprocess.run([py, '-m', 'epubcheck', base + '.epub'], capture_output=True, text=True)
    print((r.stdout + r.stderr)[-1500:])

if '--no-pdf' not in args:
    shutil.copy(os.path.join(HERE, 'print.css'), out)
    subprocess.run(['pandoc', meta, md, '-s', '-o', base + '_print.html', '--toc', '--toc-depth=1',
                    '--css', 'print.css', '--metadata', 'toc-title=Nilalaman',
                    '-V', f"header-includes=<div class='cover'><img src='img/cover_print.jpg'></div>"], check=True, cwd=out)
    subprocess.run(['node', os.path.join(HERE, 'pdf.cjs'), base + '_print.html', base + '_6x9.pdf'], check=True)
    print('PDF', base + '_6x9.pdf', os.path.getsize(base + '_6x9.pdf') // 1024, 'KB')
