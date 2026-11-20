#!/usr/bin/env python3
"""BACKUP picture source: real, high-resolution photographs from the Unsplash API (free demo tier: 50 requests an hour).
For mockups, cover and page backgrounds, and as a look at a REAL place before a prompt is written. It is not a drawing
engine: a photograph never stands in for one of the series' drawn stills without the owner's word.

usage (from history-indio/):
  unsplash_backup.py search "<words>" <out_dir> [--n 8] [--orientation portrait|landscape|squarish]
        -> <out_dir>/results.json (id, description, photographer, links), small previews and sheet.jpg to choose from   (1 request)
  unsplash_backup.py get <photo_id> <out.jpg> [--w 1080]
        -> the photograph at that width and <out>.credit.txt with the credit line                                      (2 requests)
  unsplash_backup.py limit            -> how many requests are left this hour                                              (1 request)

The key: an Unsplash "Access Key" (unsplash.com/developers, a free demo app). NEVER put it in a file, a commit or the chat.
The owner saves it in the cloud environment's settings, either as a network secret for api.unsplash.com (header
Authorization, value "Client-ID <the key>"), which the proxy then adds by itself, or as the environment variable
UNSPLASH_ACCESS_KEY, which this tool reads. Without a key the API answers 401 and this tool says so.

Rules that come with the photographs (Unsplash API guidelines and licence):
- credit the photographer and Unsplash wherever the photograph is shown ("Photo by <name> on Unsplash"): the credit line
  is written beside every download; put it in the caption or the page;
- `get` tells Unsplash about the download, as the guidelines ask; do not fetch the image file any other way;
- free to use, also commercially; never sell a photograph as it is, and never collect them to rebuild a photo service;
- photographs and credit files stay OUT of the repository (it is public): keep them in the scratchpad."""
import json, os, sys, urllib.request, urllib.parse, urllib.error

API = 'https://api.unsplash.com'
UTM = 'utm_source=history_indio&utm_medium=referral'


def _req(url):
    key = os.environ.get('UNSPLASH_ACCESS_KEY') or 'proxy-adds-the-key'      # a network secret saved in the environment replaces this header
    r = urllib.request.Request(url, headers={'Authorization': 'Client-ID ' + key, 'Accept-Version': 'v1', 'User-Agent': 'history-indio-backup/1.0'})
    try:
        with urllib.request.urlopen(r, timeout=60) as f: return json.load(f), dict(f.headers)
    except urllib.error.HTTPError as e:
        body = e.read()[:200].decode('utf-8', 'replace')
        if e.code == 401: sys.exit('Unsplash answered 401: no valid Access Key. The owner saves it in the environment settings (network secret for api.unsplash.com: '
                                   'header Authorization, value "Client-ID <key>"; or the variable UNSPLASH_ACCESS_KEY). Never in a file or the chat.')
        if e.code == 403 and 'Rate Limit' in body: sys.exit('Unsplash: the 50 requests of this hour are used up; try again in the next hour.')
        sys.exit('Unsplash answered %d: %s' % (e.code, body))


def _left(h): return h.get('X-Ratelimit-Remaining') or h.get('x-ratelimit-remaining') or '?'


def credit(p): return 'Photo by %s on Unsplash (%s?%s)' % (p['user']['name'], p['links']['html'], UTM)


def search(words, out, n=8, orientation='portrait'):
    from PIL import Image, ImageDraw
    os.makedirs(out, exist_ok=True)
    d, h = _req(API + '/search/photos?' + urllib.parse.urlencode({'query': words, 'per_page': n, 'orientation': orientation, 'content_filter': 'high'}))
    rows = [{'id': p['id'], 'description': p.get('description') or p.get('alt_description') or '', 'photographer': p['user']['name'], 'page': p['links']['html'],
             'size': [p['width'], p['height']], 'credit': credit(p), 'small': p['urls']['small']} for p in d.get('results', [])]
    json.dump({'query': words, 'total': d.get('total'), 'results': rows}, open(out + '/results.json', 'w'), ensure_ascii=False, indent=1); ims = []
    for i, r in enumerate(rows):                                               # previews come from the image server and do not count against the 50
        p = '%s/p%02d_%s.jpg' % (out, i, r['id'])
        try: urllib.request.urlretrieve(r['small'], p)
        except Exception as e: print('preview failed', r['id'], e); continue
        im = Image.open(p).convert('RGB'); im.thumbnail((300, 450)); c = Image.new('RGB', (300, 480), (20, 20, 20)); c.paste(im, ((300 - im.width) // 2, 0))
        ImageDraw.Draw(c).text((4, 456), '%d  %s  %s' % (i, r['id'], r['photographer'][:22]), fill=(255, 255, 0)); ims.append(c)
    if ims:
        sh = Image.new('RGB', (300 * min(4, len(ims)), 480 * ((len(ims) + 3) // 4)), (20, 20, 20))
        for i, c in enumerate(ims): sh.paste(c, ((i % 4) * 300, (i // 4) * 480))
        sh.save(out + '/sheet.jpg', quality=88)
    print('%d of %s photographs for "%s"; sheet: %s/sheet.jpg; requests left this hour: %s' % (len(rows), d.get('total'), words, out, _left(h)))
    for i, r in enumerate(rows): print(' %d  %s  %dx%d  %s | %s' % (i, r['id'], r['size'][0], r['size'][1], r['photographer'], r['description'][:70]))


def get(pid, out, w=1080):
    p, h = _req(API + '/photos/' + urllib.parse.quote(pid))
    url = p['urls']['raw'] + ('&' if '?' in p['urls']['raw'] else '?') + urllib.parse.urlencode({'w': w, 'q': 88, 'fm': 'jpg', 'fit': 'max'})
    urllib.request.urlretrieve(url, out)
    _req(p['links']['download_location'])                                      # the guidelines ask every app to report a download
    open(os.path.splitext(out)[0] + '.credit.txt', 'w', encoding='utf-8').write(credit(p) + '\n' + (p.get('description') or p.get('alt_description') or '') + '\n')
    print('saved %s (%d px wide) | %s | requests left this hour: about %s' % (out, w, credit(p), _left(h)))


if __name__ == '__main__':
    a = sys.argv[1:]; opt = lambda k, dflt: a[a.index(k) + 1] if k in a else dflt
    if a[:1] == ['search'] and len(a) >= 3: search(a[1], a[2].rstrip('/'), int(opt('--n', 8)), opt('--orientation', 'portrait'))
    elif a[:1] == ['get'] and len(a) >= 3: get(a[1], a[2], int(opt('--w', 1080)))
    elif a[:1] == ['limit']: d, h = _req(API + '/photos?per_page=1'); print('requests left this hour:', _left(h), 'of', h.get('X-Ratelimit-Limit') or h.get('x-ratelimit-limit') or '?')
    else: sys.exit(__doc__)
