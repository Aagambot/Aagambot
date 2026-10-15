#!/usr/bin/env python3
"""
Prepare a photo or avatar for clean ASCII conversion:
  1. Remove background / composite onto clean white canvas
  2. Tone stretch and boost edge contrast
  3. Crop square around subject

If `rembg` and `cv2` are installed, uses advanced segmentation and CLAHE.
Otherwise falls back to Pillow-native contrast stretching.

Output: source-prepped.png (grayscale), consumed by make_ascii_svg.py.

    python scripts/prep_photo.py [input.png] [output.png]
"""
import os
import sys
import numpy as np
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")

def find_input_file():
    if len(sys.argv) > 1:
        return sys.argv[1]
    repo_root = os.path.join(HERE, "..")
    candidates = [
        "source-photo.jpg",
        "source-photo.jpeg",
        "source-photo.png",
        "source-photo.webp",
    ]
    for c in candidates:
        p = os.path.join(repo_root, c)
        if os.path.exists(p):
            return p
    return os.path.join(repo_root, "source-photo.png")

INP = find_input_file()

has_cv2_rembg = False
try:
    import cv2
    from rembg import remove
    has_cv2_rembg = True
except ImportError:
    has_cv2_rembg = False


def prep_with_rembg(inp_path, out_path):
    print("Using rembg + cv2 pipeline...")
    LINE_WEIGHT = 0.6
    cut = remove(Image.open(inp_path).convert("RGBA"))
    rgb = np.array(cut.convert("RGB"))
    alpha = np.array(cut.split()[-1])
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    smooth = gray
    for _ in range(3):
        smooth = cv2.bilateralFilter(smooth, 9, 40, 9)

    valid_mask = alpha > 128
    if np.any(valid_mask):
        lo, hi = np.percentile(smooth[valid_mask], [2, 92])
        tone = np.clip((smooth.astype(np.float32) - lo) / max(hi - lo, 1), 0, 1)
    else:
        tone = smooth.astype(np.float32) / 255.0

    fine = cv2.GaussianBlur(smooth, (0, 0), 1.5).astype(np.float32)
    coarse = cv2.GaussianBlur(smooth, (0, 0), 6).astype(np.float32)
    lines = np.clip((coarse - fine) / 40.0, 0, 1)
    out = np.clip(tone - LINE_WEIGHT * lines, 0, 1) * 255

    mask = cv2.GaussianBlur(alpha.astype(np.float32) / 255.0, (0, 0), 1.0)
    out = out * mask + 255.0 * (1.0 - mask)

    ys, xs = np.where(alpha > 20)
    if len(xs) > 0 and len(ys) > 0:
        side = max(xs.max() - xs.min(), ys.max() - ys.min()) + 60
        cx, cy = (xs.min() + xs.max()) // 2, (ys.min() + ys.max()) // 2
    else:
        side = max(out.shape[0], out.shape[1])
        cx, cy = out.shape[1] // 2, out.shape[0] // 2

    canvas = np.full((side, side), 255, np.uint8)
    x0, y0 = cx - side // 2, cy - side // 2
    sx0, sy0 = max(x0, 0), max(y0, 0)
    sx1, sy1 = min(x0 + side, out.shape[1]), min(y0 + side, out.shape[0])
    canvas[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = out[sy0:sy1, sx0:sx1].astype(np.uint8)

    Image.fromarray(canvas, mode="L").save(out_path)
    print("wrote", out_path, canvas.shape)


def prep_with_pil(inp_path, out_path):
    print("Using Pillow-native pipeline (install rembg + opencv-python for AI cutout)...")
    im = Image.open(inp_path)
    
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        im_rgba = im.convert("RGBA")
        canvas = Image.new("RGB", im_rgba.size, (255, 255, 255))
        canvas.paste(im_rgba, mask=im_rgba.split()[-1])
        im = canvas
    else:
        im = im.convert("RGB")

    # Grayscale
    gray = im.convert("L")
    # Increase contrast & sharpen edges
    gray = ImageOps.autocontrast(gray, cutoff=2)
    gray = ImageEnhance.Sharpness(gray).enhance(1.8)
    gray = ImageEnhance.Contrast(gray).enhance(1.2)

    # Square crop center
    w, h = gray.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    cropped = gray.crop((left, top, left + side, top + side))

    cropped.save(out_path)
    print("wrote", out_path, cropped.size)


if __name__ == "__main__":
    if not os.path.exists(INP):
        print(f"Error: {INP} does not exist. Provide an image or place source-photo.png in repo root.", file=sys.stderr)
        sys.exit(1)
    if has_cv2_rembg:
        prep_with_rembg(INP, OUT)
    else:
        prep_with_pil(INP, OUT)
