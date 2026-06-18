"""
VigilanceAI — License Plate OCR Module
Detects license plate regions and extracts text using EasyOCR.
Optimized for Indian number plates (white/yellow background, black text).
"""

import re
import cv2
import numpy as np
from typing import Optional, List, Tuple
import easyocr

from config import (
    OCR_LANGUAGES, OCR_MIN_TEXT_LENGTH,
    OCR_PLATE_PATTERN, PLATE_CONFIDENCE_THRESHOLD
)
from detection.detector import BBox


class PlateReader:

    def __init__(self):
        print("[VigilanceAI] Initializing EasyOCR...")
        self.reader = easyocr.Reader(OCR_LANGUAGES, gpu=False, verbose=False)
        self._plate_pattern = re.compile(OCR_PLATE_PATTERN)
        print("[VigilanceAI] EasyOCR ready ✓")

    def _detect_plate_region(self, img, vehicle_bbox=None):
        h, w = img.shape[:2]
        if vehicle_bbox:
            x1 = max(0, int(vehicle_bbox.x1))
            y1 = max(0, int(vehicle_bbox.y1))
            x2 = min(w, int(vehicle_bbox.x2))
            y2 = min(h, int(vehicle_bbox.y2))
            search_img = img[y1:y2, x1:x2]
        else:
            search_img = img

        plates = []
        hsv = cv2.cvtColor(search_img, cv2.COLOR_BGR2HSV)
        white_mask = cv2.inRange(hsv,
            np.array([0, 0, 180]),
            np.array([180, 40, 255])
        )
        yellow_mask = cv2.inRange(hsv,
            np.array([20, 100, 100]),
            np.array([35, 255, 255])
        )
        combined = cv2.bitwise_or(white_mask, yellow_mask)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
        combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(
            combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        sh, sw = search_img.shape[:2]
        for cnt in contours:
            x, y, cw, ch = cv2.boundingRect(cnt)
            aspect = cw / ch if ch > 0 else 0
            area_ratio = (cw * ch) / (sw * sh)
            if 1.5 < aspect < 6.0 and 0.005 < area_ratio < 0.25:
                pad_x, pad_y = int(cw * 0.1), int(ch * 0.2)
                rx1 = max(0, x - pad_x)
                ry1 = max(0, y - pad_y)
                rx2 = min(sw, x + cw + pad_x)
                ry2 = min(sh, y + ch + pad_y)
                plate_roi = search_img[ry1:ry2, rx1:rx2]
                if plate_roi.size > 0:
                    plates.append(plate_roi)
        return plates

    def _enhance_plate(self, plate_roi):
        h, w = plate_roi.shape[:2]
        scale = 60 / h if h > 0 else 1
        resized = cv2.resize(
            plate_roi, (int(w * scale), 60),
            interpolation=cv2.INTER_CUBIC
        )
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(4, 4))
        enhanced = clahe.apply(gray)
        _, binary = cv2.threshold(
            enhanced, 0, 255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        return binary

    def _parse_plate_text(self, raw_texts):
        combined = "".join(
            t.upper().replace(" ", "").replace("-", "")
            for t, conf in raw_texts
            if conf > PLATE_CONFIDENCE_THRESHOLD
        )
        match = self._plate_pattern.search(combined)
        if match:
            return match.group()
        clean = re.sub(r"[^A-Z0-9]", "", combined)
        if len(clean) >= OCR_MIN_TEXT_LENGTH:
            return clean
        return None

    def read_plate(self, img, vehicle_bbox=None):
        plate_candidates = self._detect_plate_region(img, vehicle_bbox)
        for plate_roi in plate_candidates:
            enhanced = self._enhance_plate(plate_roi)
            results = self.reader.readtext(enhanced, detail=1, paragraph=False)
            texts = [(text, conf) for (_, text, conf) in results]
            plate_text = self._parse_plate_text(texts)
            if plate_text:
                return plate_text
        if vehicle_bbox and not plate_candidates:
            h, w = img.shape[:2]
            x1, y1 = max(0, int(vehicle_bbox.x1)), max(0, int(vehicle_bbox.y1))
            x2, y2 = min(w, int(vehicle_bbox.x2)), min(h, int(vehicle_bbox.y2))
            crop = img[y1:y2, x1:x2]
            if crop.size > 0:
                results = self.reader.readtext(crop, detail=1, paragraph=False)
                texts = [(text, conf) for (_, text, conf) in results]
                return self._parse_plate_text(texts)
        return None

    def read_plates_for_violations(self, img, vehicle_bboxes):
        results = {}
        for i, bbox in enumerate(vehicle_bboxes):
            results[i] = self.read_plate(img, bbox)
        return results
