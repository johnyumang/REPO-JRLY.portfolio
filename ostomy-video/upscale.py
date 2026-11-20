#!/usr/bin/env python3
"""4x AI upscale with Real-ESRGAN general-x4v3 (xinntao/Real-ESRGAN, BSD-3; ONNX export with a fixed 128x128 input,
`tamnvcc/Real-ESRGAN-General-x4v3_float` on Hugging Face). Runs on CPU. The picture is cut into overlapping 128 px
tiles, each is upscaled, and the overlaps are feathered together.
usage as a tool: upscale.py MODEL.onnx IN.png OUT.png"""
import os, sys
import numpy as np
import onnxruntime as ort


class Upscaler:
    T, OV = 128, 16

    def __init__(self, path):
        so = ort.SessionOptions()
        so.intra_op_num_threads = os.cpu_count()
        self.s = ort.InferenceSession(path, so, providers=["CPUExecutionProvider"])
        self.n = self.s.get_inputs()[0].name
        r = np.minimum(np.arange(self.T * 4) + 0.5, self.T * 4 - np.arange(self.T * 4) - 0.5) / (self.OV * 4)
        self.w = np.clip(np.minimum.outer(r, r), 0.02, 1)[..., None].astype(np.float32)        # feather for the overlaps

    def __call__(self, img):
        """uint8 HxWx3 -> uint8 4Hx4Wx3"""
        h, w = img.shape[:2]
        x = img.astype(np.float32) / 255
        ys = np.unique(np.linspace(0, h - self.T, int(np.ceil((h - self.OV) / (self.T - self.OV)))).round().astype(int))
        xs = np.unique(np.linspace(0, w - self.T, int(np.ceil((w - self.OV) / (self.T - self.OV)))).round().astype(int))
        acc = np.zeros((h * 4, w * 4, 3), np.float32)
        wsum = np.zeros((h * 4, w * 4, 1), np.float32)
        for y0 in ys:
            for x0 in xs:
                t = x[y0:y0 + self.T, x0:x0 + self.T].transpose(2, 0, 1)[None]
                o = self.s.run(None, {self.n: t})[0][0].transpose(1, 2, 0)
                acc[y0 * 4:(y0 + self.T) * 4, x0 * 4:(x0 + self.T) * 4] += o * self.w
                wsum[y0 * 4:(y0 + self.T) * 4, x0 * 4:(x0 + self.T) * 4] += self.w
        return (np.clip(acc / wsum, 0, 1) * 255).astype(np.uint8)


if __name__ == "__main__":
    from PIL import Image
    Image.fromarray(Upscaler(sys.argv[1])(np.asarray(Image.open(sys.argv[2]).convert("RGB")))).save(sys.argv[3])
