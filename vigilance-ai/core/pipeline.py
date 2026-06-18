"""
VigilanceAI — Main Pipeline
Single entry point that wires preprocessing → detection → OCR → evidence.
"""

import cv2
import numpy as np
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

sys.path.insert(0, str(Path(__file__).parent))

from preprocessing.enhancer import preprocess_from_path, preprocess
from detection.detector import ViolationDetector
from ocr.plate_reader import PlateReader
from output.annotator import EvidenceGenerator


class VigilancePipeline:

    def __init__(
        self,
        yolo_model: str = "yolov8n.pt",
        enable_ocr: bool = True,
        output_dir: str = "output/evidence",
        camera_id: str = "CAM-001",
        location: str = "Bengaluru, Karnataka"
    ):
        self.detector  = ViolationDetector(yolo_model)
        self.ocr       = PlateReader() if enable_ocr else None
        self.evidence  = EvidenceGenerator(output_dir)
        self.camera_id = camera_id
        self.location  = location

    def analyze_image(self, image_path: str, has_stop_line: bool = False, save_output: bool = True) -> Dict[str, Any]:
        from preprocessing.enhancer import preprocess_from_path
        original, preprocessed = preprocess_from_path(image_path)

        analysis = self.detector.analyze(preprocessed, has_stop_line=has_stop_line)

        if self.ocr and analysis.violations:
            vehicle_bboxes = [
                v.bbox for v in analysis.violations
                if any(d.category == "vehicle" for d in v.associated_detections)
            ]
            plate_map = self.ocr.read_plates_for_violations(preprocessed, vehicle_bboxes)
            for i, v in enumerate(analysis.violations):
                if i in plate_map and plate_map[i]:
                    v.license_plate = plate_map[i]

        ev = self.evidence.generate(
            original_img=original,
            preprocessed_img=preprocessed,
            analysis=analysis,
            source_path=image_path,
            camera_id=self.camera_id,
            location=self.location,
        )

        if save_output:
            paths = self.evidence.save_evidence(ev)
            ev["saved_paths"] = paths

        return ev

    def analyze_from_numpy(self, img_bgr: np.ndarray, has_stop_line: bool = False) -> Dict[str, Any]:
        preprocessed = preprocess(img_bgr)
        analysis = self.detector.analyze(preprocessed, has_stop_line=has_stop_line)

        if self.ocr and analysis.violations:
            vehicle_bboxes = [
                v.bbox for v in analysis.violations
                if any(d.category == "vehicle" for d in v.associated_detections)
            ]
            plate_map = self.ocr.read_plates_for_violations(preprocessed, vehicle_bboxes)
            for i, v in enumerate(analysis.violations):
                if i in plate_map and plate_map[i]:
                    v.license_plate = plate_map[i]

        ev = self.evidence.generate(
            original_img=img_bgr,
            preprocessed_img=preprocessed,
            analysis=analysis,
            camera_id=self.camera_id,
            location=self.location,
        )
        return ev

    def to_api_response(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        return self.evidence.to_api_response(evidence)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <image_path> [--stop-line]")
        sys.exit(1)

    img_path  = sys.argv[1]
    stop_line = "--stop-line" in sys.argv

    print(f"\n{'='*55}")
    print("  VigilanceAI — Traffic Violation Analysis System")
    print(f"{'='*55}\n")

    pipeline = VigilancePipeline()
    result   = pipeline.analyze_image(img_path, has_stop_line=stop_line)
    meta     = result["metadata"]

    print(f"  Incident ID : {meta['incident_id']}")
    print(f"  Timestamp   : {meta['timestamp']}")
    print(f"  Vehicles    : {meta['total_vehicles']}")
    print(f"  Persons     : {meta['total_persons']}")
    print(f"  Violations  : {meta['violation_count']}")

    if meta["violations"]:
        print("\n  Violations Detected:")
        for v in meta["violations"]:
            plate = v.get("license_plate") or "N/A"
            print(f"    ▸ [{v['severity']}] {v['violation_label']} "
                  f"(conf: {v['confidence']:.0%}) | Plate: {plate}")
    else:
        print("\n  No violations detected.")

    if "saved_paths" in result:
        print(f"\n  Evidence saved:")
        print(f"    Image : {result['saved_paths']['annotated_image']}")
        print(f"    JSON  : {result['saved_paths']['metadata_json']}")

    print(f"\n{'='*55}\n")
