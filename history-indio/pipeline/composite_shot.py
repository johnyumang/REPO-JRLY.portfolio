"""Put a character (drawn on a plain white background) over a scene's single background plate.
usage: composite_shot.py character.jpg plate.jpg out.jpg [crop_x crop_y crop_scale blur]
The same plate is reused for every shot of a scene, so the background is identical across shots."""
import sys, cv2, numpy as np

def cutout(im):
    white = (im.min(axis=2) > 225).astype(np.uint8)
    _, lab = cv2.connectedComponents(white)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    m = np.isin(lab, list(border)).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((7, 7), np.uint8))          # eat the white fringe
    return (255 - cv2.GaussianBlur(m, (5, 5), 0)).astype(np.float32) / 255

def composite(char, plate, x=0.0, y=0.0, s=1.0, blur=4.0, tint=(1.05, 0.92, 0.86), gain=0.92):
    H, W = char.shape[:2]
    plate = cv2.resize(plate, (W, H))
    cw, ch = int(W * s), int(H * s)
    x0, y0 = int((W - cw) * x), int((H - ch) * y)
    b = cv2.resize(plate[y0:y0 + ch, x0:x0 + cw], (W, H), interpolation=cv2.INTER_CUBIC)
    if blur: b = cv2.GaussianBlur(b, (0, 0), blur)
    a = cutout(char)[..., None]
    c = np.clip(char.astype(np.float32) * np.array(tint) * gain, 0, 255)   # tint is BGR
    return (b * (1 - a) + c * a).astype(np.uint8)

if __name__ == '__main__':
    a = sys.argv
    x, y, s, bl = (list(map(float, a[4:8])) + [0, 0, 1, 4][len(a[4:8]):])
    cv2.imwrite(a[3], composite(cv2.imread(a[1]), cv2.imread(a[2]), x, y, s, bl), [cv2.IMWRITE_JPEG_QUALITY, 93])
