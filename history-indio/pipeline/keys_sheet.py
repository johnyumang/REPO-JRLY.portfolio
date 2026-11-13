#!/usr/bin/env python3
"""Contact sheet of an episode's keys, one numbered thumbnail per shot of key_prompts.json (falls back to the still in full/).
usage: keys_sheet.py videos/<slug> <out.jpg> [columns]"""
import cv2, numpy as np, sys, os, json
v=sys.argv[1]; out=sys.argv[2]; cols=int(sys.argv[3]) if len(sys.argv)>3 else 7
K=json.load(open(v+'/key_prompts.json')); shots=K['shots']
W,H=216,384; cells=[]
for k in sorted(shots):
    sh=shots[k]; name=sh.get('full') or sh.get('char') or sh.get('plate')
    p=None
    for e in ('png','jpg'):
        for pat in (f'{v}/keys/k{k}.{e}', f'{v}/keys/{k}.{e}'):
            if os.path.exists(pat): p=pat
    if p is None:
        for e in ('png','jpg'):
            if os.path.exists(f'{v}/full/{name}.{e}'): p=f'{v}/full/{name}.{e}'
    im=cv2.imread(p) if p else None
    if im is None: im=np.zeros((H,W,3),np.uint8)
    im=cv2.resize(im,(W,H),interpolation=cv2.INTER_AREA)
    cv2.rectangle(im,(0,0),(W,22),(0,0,0),-1); cv2.putText(im,f'{k} {name}'[:26],(3,16),cv2.FONT_HERSHEY_SIMPLEX,0.42,(255,255,255),1,cv2.LINE_AA)
    cells.append(im)
while len(cells)%cols: cells.append(np.zeros((H,W,3),np.uint8))
rows=[np.hstack(cells[i:i+cols]) for i in range(0,len(cells),cols)]
cv2.imwrite(out,np.vstack(rows),[cv2.IMWRITE_JPEG_QUALITY,82]); print(out,len(shots))
