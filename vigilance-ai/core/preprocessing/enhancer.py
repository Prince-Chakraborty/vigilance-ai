"""
VigilanceAI — Preprocessing Module
Handles image enhancement for robust detection under real-world conditions:
low light, rain, shadows, motion blur, CCTV compression artifacts.
"""

import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional
from config import (
    CLAHE_CLIP_LIMIT, CLAHE_TILE_GRID,
    DENOISE_H, DENOISE_TEMPLATE_WS, DENOISE_SEARCH_WS
)


def load_image(path: str) -> np.ndarray:
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {path}")
    return img


def pil_to_cv2(pil_img: Image.Image) -> np.ndarray:
    arr = np.array(pil_img.convert("RGB"))
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def cv2_to_pil(cv2_img: np.ndarray) -> Image.Image:
    rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def apply_clahe(img: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(
        clipLimit=CLAHE_CLIP_LIMIT,
        tileGridSize=CLAHE_TILE_GRID
    )
    l_enhanced = clahe.apply(l)
    enhanced = cv2.merge([l_enhanced, a, b])
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)


def denoise(img: np.ndarray) -> np.ndarray:
    return cv2.fastNlMeansDenoisingColored(
        img, None,
        DENOISE_H, DENOISE_H,
        DENOISE_TEMPLATE_WS, DENOISE_SEARCH_WS
    )


def sharpen(img: np.ndarray) -> np.ndarray:
    gaussian = cv2.GaussianBlur(img, (0, 0), 2.0)
    return cv2.addWeighted(img, 1.5, gaussian, -0.5, 0)


def gamma_correction(img: np.ndarray, gamma: float = 1.2) -> np.ndarray:
    inv_gamma = 1.0 / gamma
    table = np.array([
        ((i / 255.0) ** inv_gamma) * 255
        for i in range(256)
    ], dtype=np.uint8)
    return cv2.LUT(img, table)


def detect_low_light(img: np.ndarray, threshold: int = 60) -> bool:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return float(gray.mean()) < threshold


def detect_blur(img: np.ndarray, threshold: float = 80.0) -> bool:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var()) < threshold


def normalize(img: np.ndarray) -> np.ndarray:
    return cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)


def resize_for_inference(
    img: np.ndarray,
    target_size: Tuple[int, int] = (640, 640),
    keep_aspect: bool = True
) -> Tuple[np.ndarray, float, Tuple[int, int]]:
    h, w = img.shape[:2]
    th, tw = target_size

    if keep_aspect:
        scale = min(tw / w, th / h)
        new_w, new_h = int(w * scale), int(h * scale)
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        pad_top  = (th - new_h) // 2
        pad_left = (tw - new_w) // 2
        padded = cv2.copyMakeBorder(
            resized, pad_top, th - new_h - pad_top,
            pad_left, tw - new_w - pad_left,
            cv2.BORDER_CONSTANT, value=(114, 114, 114)
        )
        return padded, scale, (pad_top, pad_left)
    else:
        return cv2.resize(img, (tw, th)), 1.0, (0, 0)


def preprocess(
    img: np.ndarray,
    enable_clahe: bool = True,
    enable_denoise: bool = False,
    enable_sharpen: bool = True,
    enable_gamma: bool = True,
) -> np.ndarray:
    out = img.copy()
    if enable_gamma and detect_low_light(out):
        out = gamma_correction(out, gamma=1.4)
    if enable_clahe:
        out = apply_clahe(out)
    if enable_denoise:
        out = denoise(out)
    if enable_sharpen and detect_blur(out):
        out = sharpen(out)
    return out


def preprocess_from_path(path: str, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
    original = load_image(path)
    processed = preprocess(original, **kwargs)
    return original, processed


def preprocess_from_pil(pil_img: Image.Image, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
    original = pil_to_cv2(pil_img)
    processed = preprocess(original, **kwargs)
    return original, processed
