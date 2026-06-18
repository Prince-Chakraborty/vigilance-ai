"""
VigilanceAI — Detection Engine
YOLOv8-based multi-class vehicle/person detection with heuristic
violation classification on top of raw detections.
"""

import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from ultralytics import YOLO

from config import (
    VEHICLE_CLASSES, PERSON_CLASSES, ALL_TRACKED_CLASSES,
    DETECTION_CONFIDENCE_THRESHOLD, NMS_IOU_THRESHOLD,
    VIOLATION_COLORS, VIOLATION_SEVERITY, VIOLATION_LABELS,
    TRIPLE_RIDING_PERSON_THRESHOLD,
    WRONG_SIDE_LANE_RATIO,
    STOP_LINE_Y_RATIO,
    TRAFFIC_LIGHT_ROI_RATIO,
)


@dataclass
class BBox:
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def cx(self) -> float:
        return (self.x1 + self.x2) / 2

    @property
    def cy(self) -> float:
        return (self.y1 + self.y2) / 2

    @property
    def area(self) -> float:
        return max(0, self.x2 - self.x1) * max(0, self.y2 - self.y1)

    def iou(self, other: "BBox") -> float:
        ix1 = max(self.x1, other.x1)
        iy1 = max(self.y1, other.y1)
        ix2 = min(self.x2, other.x2)
        iy2 = min(self.y2, other.y2)
        inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
        union = self.area + other.area - inter
        return inter / union if union > 0 else 0.0

    def contains_center(self, other: "BBox") -> bool:
        return (self.x1 <= other.cx <= self.x2 and
                self.y1 <= other.cy <= self.y2)


@dataclass
class Detection:
    bbox:       BBox
    class_id:   int
    class_name: str
    confidence: float
    category:   str


@dataclass
class ViolationResult:
    violation_type:  str
    violation_label: str
    severity:        str
    confidence:      float
    bbox:            BBox
    associated_detections: List[Detection] = field(default_factory=list)
    license_plate:   Optional[str] = None
    notes:           str = ""


@dataclass
class FrameAnalysis:
    detections:   List[Detection]
    violations:   List[ViolationResult]
    frame_width:  int
    frame_height: int
    has_red_light: bool = False
    has_stop_line: bool = False


class ViolationDetector:

    def __init__(self, model_path: str = "yolov8n.pt"):
        print(f"[VigilanceAI] Loading YOLO model: {model_path}")
        self.model = YOLO(model_path)
        print("[VigilanceAI] Model loaded ✓")

    def _run_yolo(self, img: np.ndarray) -> List[Detection]:
        results = self.model(
            img,
            conf=DETECTION_CONFIDENCE_THRESHOLD,
            iou=NMS_IOU_THRESHOLD,
            verbose=False
        )
        detections = []
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                if cls_id not in ALL_TRACKED_CLASSES:
                    continue
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls_name = ALL_TRACKED_CLASSES[cls_id]
                category = "vehicle" if cls_id in VEHICLE_CLASSES else "person"
                detections.append(Detection(
                    bbox=BBox(x1, y1, x2, y2),
                    class_id=cls_id,
                    class_name=cls_name,
                    confidence=conf,
                    category=category
                ))
        return detections

    def _check_helmet_compliance(self, detections, img):
        violations = []
        motorcycles = [d for d in detections if d.class_name == "motorcycle"]
        persons = [d for d in detections if d.category == "person"]
        for moto in motorcycles:
            riders = [p for p in persons if moto.bbox.iou(p.bbox) > 0.15
                      or moto.bbox.contains_center(p.bbox)]
            if not riders:
                continue
            for rider in riders:
                head_region = self._extract_head_roi(img, rider.bbox)
                if head_region is not None and not self._has_helmet(head_region):
                    violations.append(ViolationResult(
                        violation_type="helmet_non_compliance",
                        violation_label=VIOLATION_LABELS["helmet_non_compliance"],
                        severity=VIOLATION_SEVERITY["helmet_non_compliance"],
                        confidence=round(moto.confidence * 0.85, 3),
                        bbox=rider.bbox,
                        associated_detections=[moto, rider],
                        notes="Rider detected without helmet"
                    ))
        return violations

    def _extract_head_roi(self, img, person_bbox):
        h, w = img.shape[:2]
        x1 = max(0, int(person_bbox.x1))
        y1 = max(0, int(person_bbox.y1))
        x2 = min(w, int(person_bbox.x2))
        head_h = max(1, int((person_bbox.y2 - person_bbox.y1) * 0.30))
        y2 = min(h, y1 + head_h)
        roi = img[y1:y2, x1:x2]
        return roi if roi.size > 0 else None

    def _has_helmet(self, head_roi):
        gray = cv2.cvtColor(head_roi, cv2.COLOR_BGR2GRAY)
        dark_pixels = np.sum(gray < 120)
        total_pixels = gray.size
        ratio = dark_pixels / total_pixels if total_pixels > 0 else 0
        return ratio > 0.35

    def _check_triple_riding(self, detections):
        violations = []
        motorcycles = [d for d in detections if d.class_name == "motorcycle"]
        persons = [d for d in detections if d.category == "person"]
        for moto in motorcycles:
            riders = [p for p in persons
                      if moto.bbox.iou(p.bbox) > 0.10
                      or moto.bbox.contains_center(p.bbox)]
            if len(riders) >= TRIPLE_RIDING_PERSON_THRESHOLD:
                violations.append(ViolationResult(
                    violation_type="triple_riding",
                    violation_label=VIOLATION_LABELS["triple_riding"],
                    severity=VIOLATION_SEVERITY["triple_riding"],
                    confidence=round(moto.confidence * 0.90, 3),
                    bbox=moto.bbox,
                    associated_detections=[moto] + riders,
                    notes=f"{len(riders)} persons detected on single motorcycle"
                ))
        return violations

    def _check_wrong_side_driving(self, detections, frame_width):
        violations = []
        threshold_x = frame_width * WRONG_SIDE_LANE_RATIO
        for v in [d for d in detections if d.category == "vehicle"]:
            if v.bbox.cx < threshold_x:
                violations.append(ViolationResult(
                    violation_type="wrong_side_driving",
                    violation_label=VIOLATION_LABELS["wrong_side_driving"],
                    severity=VIOLATION_SEVERITY["wrong_side_driving"],
                    confidence=round(v.confidence * 0.75, 3),
                    bbox=v.bbox,
                    associated_detections=[v],
                    notes="Vehicle centroid detected in oncoming lane"
                ))
        return violations

    def _check_stop_line_violation(self, detections, frame_height, has_stop_line):
        violations = []
        if not has_stop_line:
            return violations
        stop_y = frame_height * STOP_LINE_Y_RATIO
        for v in [d for d in detections if d.category == "vehicle"]:
            if v.bbox.y2 > stop_y:
                violations.append(ViolationResult(
                    violation_type="stop_line_violation",
                    violation_label=VIOLATION_LABELS["stop_line_violation"],
                    severity=VIOLATION_SEVERITY["stop_line_violation"],
                    confidence=round(v.confidence * 0.80, 3),
                    bbox=v.bbox,
                    associated_detections=[v],
                    notes="Vehicle crossed estimated stop line"
                ))
        return violations

    def _check_red_light_violation(self, detections, img, has_stop_line):
        h, w = img.shape[:2]
        r1, c1, r2, c2 = TRAFFIC_LIGHT_ROI_RATIO
        roi = img[int(h*r1):int(h*r2), int(w*c1):int(w*c2)]
        is_red = self._detect_red_in_roi(roi)
        violations = []
        if is_red and has_stop_line:
            stop_y = h * STOP_LINE_Y_RATIO
            for v in [d for d in detections if d.category == "vehicle"]:
                if v.bbox.y2 > stop_y:
                    violations.append(ViolationResult(
                        violation_type="red_light_violation",
                        violation_label=VIOLATION_LABELS["red_light_violation"],
                        severity=VIOLATION_SEVERITY["red_light_violation"],
                        confidence=round(v.confidence * 0.85, 3),
                        bbox=v.bbox,
                        associated_detections=[v],
                        notes="Vehicle crossed stop line during red light"
                    ))
        return violations, is_red

    def _detect_red_in_roi(self, roi):
        if roi.size == 0:
            return False
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, np.array([0, 120, 70]),   np.array([10, 255, 255]))
        mask2 = cv2.inRange(hsv, np.array([160, 120, 70]), np.array([180, 255, 255]))
        red_pixels = cv2.countNonZero(mask1 | mask2)
        return red_pixels > (roi.shape[0] * roi.shape[1] * 0.05)

    def _check_illegal_parking(self, detections, frame_width, frame_height):
        violations = []
        edge_threshold = frame_width * 0.15
        for v in [d for d in detections if d.category == "vehicle"]:
            if v.bbox.x1 < edge_threshold or v.bbox.x2 > (frame_width - edge_threshold):
                violations.append(ViolationResult(
                    violation_type="illegal_parking",
                    violation_label=VIOLATION_LABELS["illegal_parking"],
                    severity=VIOLATION_SEVERITY["illegal_parking"],
                    confidence=round(v.confidence * 0.70, 3),
                    bbox=v.bbox,
                    associated_detections=[v],
                    notes="Vehicle detected in roadside/no-parking zone"
                ))
        return violations

    def _deduplicate(self, violations):
        seen = set()
        unique = []
        for v in violations:
            key = (v.violation_type, round(v.bbox.cx), round(v.bbox.cy))
            if key not in seen:
                seen.add(key)
                unique.append(v)
        return unique

    def analyze(self, img: np.ndarray, has_stop_line: bool = False) -> FrameAnalysis:
        h, w = img.shape[:2]
        detections = self._run_yolo(img)
        violations = []
        violations += self._check_helmet_compliance(detections, img)
        violations += self._check_triple_riding(detections)
        violations += self._check_wrong_side_driving(detections, w)
        violations += self._check_stop_line_violation(detections, h, has_stop_line)
        violations += self._check_illegal_parking(detections, w, h)
        rl_violations, is_red = self._check_red_light_violation(detections, img, has_stop_line)
        violations += rl_violations
        violations = self._deduplicate(violations)
        return FrameAnalysis(
            detections=detections,
            violations=violations,
            frame_width=w,
            frame_height=h,
            has_red_light=is_red,
            has_stop_line=has_stop_line
        )
