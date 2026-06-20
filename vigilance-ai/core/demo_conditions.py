"""
VigilanceAI — Robustness Demo
Generates side-by-side before/after images showing preprocessing
handles low-light, glare, and rain-like noise conditions.
"""

import sys
import cv2
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from preprocessing.enhancer import preprocess

OUT_DIR = Path("demo_output")
OUT_DIR.mkdir(exist_ok=True)


def make_base_scene(w=640, h=480):
    img = np.full((h, w, 3), 140, dtype=np.uint8)
    cv2.rectangle(img, (150, 200), (350, 340), (190, 190, 190), -1)
    cv2.rectangle(img, (400, 220), (550, 330), (170, 170, 170), -1)
    cv2.circle(img, (300, 150), 30, (100, 100, 220), -1)
    return img


def simulate_low_light(img):
    return (img * 0.25).astype(np.uint8)


def simulate_glare(img):
    out = img.copy()
    cv2.circle(out, (480, 100), 80, (255, 255, 255), -1)
    return out


def simulate_rain_noise(img):
    noise = np.random.normal(0, 25, img.shape).astype(np.int16)
    out = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    for _ in range(150):
        x, y = np.random.randint(0, img.shape[1]), np.random.randint(0, img.shape[0])
        cv2.line(out, (x, y), (x - 5, y + 15), (200, 200, 200), 1)
    return out


def side_by_side(before, after, label):
    h, w = before.shape[:2]
    canvas = np.zeros((h + 40, w * 2 + 20, 3), dtype=np.uint8)
    canvas[40:, :w] = before
    canvas[40:, w+20:] = after
    cv2.putText(canvas, f"{label} - BEFORE", (10, 25), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255,255,255), 1)
    cv2.putText(canvas, f"{label} - AFTER (preprocessed)", (w+30, 25), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0,255,150), 1)
    return canvas


def run_demo():
    base = make_base_scene()
    conditions = {
        "low_light": simulate_low_light(base),
        "glare":     simulate_glare(base),
        "rain_noise": simulate_rain_noise(base),
    }

    print("=" * 55)
    print("  VigilanceAI - Robustness Across Conditions")
    print("=" * 55)

    for name, img in conditions.items():
        processed = preprocess(img, enable_denoise=(name == "rain_noise"))
        comparison = side_by_side(img, processed, name.replace("_", " ").title())
        out_path = OUT_DIR / f"{name}_comparison.jpg"
        cv2.imwrite(str(out_path), comparison)
        print(f"  Saved: {name:12s} -> {out_path}")

    print("=" * 55)
    print(f"  All comparisons saved to: {OUT_DIR}/")
    print("=" * 55)


if __name__ == "__main__":
    run_demo()
