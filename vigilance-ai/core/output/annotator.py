"""
VigilanceAI — Output & Annotation Module
Produces annotated images with bounding boxes, violation labels,
confidence scores, and metadata for evidence generation.
"""

import cv2
import json
import uuid
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from PIL import Image

from config import (
    VIOLATION_COLORS, ANNOTATION_FONT_SCALE,
    ANNOTATION_THICKNESS, OUTPUT_IMAGE_QUALITY
)
from detection.detector import FrameAnalysis, Detection, ViolationResult


class Annotator:

    FONT       = cv2.FONT_HERSHEY_DUPLEX
    FONT_SCALE = ANNOTATION_FONT_SCALE
    THICKNESS  = ANNOTATION_THICKNESS

    def _draw_box(self, img, x1, y1, x2, y2, color, label, confidence):
        cv2.rectangle(img, (x1, y1), (x2, y2), color, self.THICKNESS)
        text = f"{label} {confidence:.0%}"
        (tw, th), _ = cv2.getTextSize(text, self.FONT, self.FONT_SCALE, self.THICKNESS)
        header_y = max(y1 - th - 8, 0)
        cv2.rectangle(img, (x1, header_y), (x1 + tw + 8, header_y + th + 8), color, -1)
        cv2.putText(
            img, text, (x1 + 4, header_y + th + 2),
            self.FONT, self.FONT_SCALE,
            (255, 255, 255), self.THICKNESS, cv2.LINE_AA
        )

    def annotate(self, img, analysis, show_all_detections=True):
        out = img.copy()
        h, w = out.shape[:2]

        if show_all_detections:
            for det in analysis.detections:
                color = VIOLATION_COLORS.get(det.category, (200, 200, 200))
                x1,y1,x2,y2 = (
                    int(det.bbox.x1), int(det.bbox.y1),
                    int(det.bbox.x2), int(det.bbox.y2)
                )
                cv2.rectangle(out, (x1,y1), (x2,y2), color, 1)
                cv2.putText(
                    out, f"{det.class_name} {det.confidence:.0%}",
                    (x1+2, y1-4), self.FONT, 0.38,
                    color, 1, cv2.LINE_AA
                )

        for v in analysis.violations:
            color = VIOLATION_COLORS.get(v.violation_type, (0, 0, 255))
            x1,y1,x2,y2 = (
                int(v.bbox.x1), int(v.bbox.y1),
                int(v.bbox.x2), int(v.bbox.y2)
            )
            self._draw_box(out, x1, y1, x2, y2, color, v.violation_label, v.confidence)
            if v.license_plate:
                cv2.putText(
                    out, f"Plate: {v.license_plate}",
                    (x1 + 4, y2 + 18), self.FONT, 0.45,
                    (0, 255, 255), 1, cv2.LINE_AA
                )

        self._draw_header(out, analysis)

        if analysis.has_red_light:
            cv2.circle(out, (w - 30, 30), 15, (0, 0, 255), -1)
            cv2.putText(out, "RED", (w - 52, 36),
                        self.FONT, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        return out

    def _draw_header(self, img, analysis):
        h, w = img.shape[:2]
        cv2.rectangle(img, (0, 0), (w, 36), (20, 20, 20), -1)
        n_viol = len(analysis.violations)
        n_det  = len(analysis.detections)
        ts     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_color = (0, 60, 255) if n_viol > 0 else (0, 180, 60)
        status_text  = f"VIOLATIONS: {n_viol}" if n_viol > 0 else "CLEAR"
        cv2.putText(img, f"VigilanceAI  |  {ts}  |  Objects: {n_det}",
                    (10, 24), self.FONT, 0.48, (200, 200, 200), 1, cv2.LINE_AA)
        cv2.putText(img, status_text,
                    (w - 200, 24), self.FONT, 0.52, status_color, 1, cv2.LINE_AA)


class EvidenceGenerator:

    def __init__(self, output_dir: str = "output/evidence"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.annotator = Annotator()

    def generate(self, original_img, preprocessed_img, analysis,
                 source_path=None, camera_id="CAM-001", location="Bengaluru, Karnataka"):
        incident_id = str(uuid.uuid4())[:8].upper()
        timestamp   = datetime.now().isoformat()
        annotated   = self.annotator.annotate(preprocessed_img, analysis)

        violation_records = []
        for v in analysis.violations:
            violation_records.append({
                "violation_type":  v.violation_type,
                "violation_label": v.violation_label,
                "severity":        v.severity,
                "confidence":      v.confidence,
                "license_plate":   v.license_plate,
                "notes":           v.notes,
                "bbox": {
                    "x1": round(v.bbox.x1, 1),
                    "y1": round(v.bbox.y1, 1),
                    "x2": round(v.bbox.x2, 1),
                    "y2": round(v.bbox.y2, 1),
                }
            })

        metadata = {
            "incident_id":      incident_id,
            "timestamp":        timestamp,
            "camera_id":        camera_id,
            "location":         location,
            "source_file":      source_path or "live_feed",
            "frame_size":       [analysis.frame_width, analysis.frame_height],
            "total_vehicles":   sum(1 for d in analysis.detections if d.category == "vehicle"),
            "total_persons":    sum(1 for d in analysis.detections if d.category == "person"),
            "violations":       violation_records,
            "violation_count":  len(violation_records),
            "red_light_active": analysis.has_red_light,
        }

        return {
            "incident_id":   incident_id,
            "annotated_img": annotated,
            "original_img":  original_img,
            "metadata":      metadata,
        }

    def save_evidence(self, evidence):
        inc_id    = evidence["incident_id"]
        img_path  = self.output_dir / f"{inc_id}_annotated.jpg"
        meta_path = self.output_dir / f"{inc_id}_metadata.json"
        cv2.imwrite(str(img_path), evidence["annotated_img"],
                    [cv2.IMWRITE_JPEG_QUALITY, OUTPUT_IMAGE_QUALITY])
        with open(meta_path, "w") as f:
            json.dump(evidence["metadata"], f, indent=2)
        return {
            "annotated_image": str(img_path),
            "metadata_json":   str(meta_path),
        }

    def to_api_response(self, evidence):
        import base64
        _, buf = cv2.imencode(".jpg", evidence["annotated_img"],
                              [cv2.IMWRITE_JPEG_QUALITY, OUTPUT_IMAGE_QUALITY])
        img_b64 = base64.b64encode(buf).decode("utf-8")
        return {
            "incident_id":          evidence["incident_id"],
            "annotated_image_b64":  img_b64,
            "metadata":             evidence["metadata"],
        }
