"""
VigilanceAI — Core Configuration
All constants, class mappings, and thresholds in one place.
"""

# ─── YOLO COCO class IDs we care about ───────────────────────────────────────
VEHICLE_CLASSES = {
    2:  "car",
    3:  "motorcycle",
    5:  "bus",
    7:  "truck",
    1:  "bicycle",
}

PERSON_CLASSES = {
    0: "person",
}

ALL_TRACKED_CLASSES = {**VEHICLE_CLASSES, **PERSON_CLASSES}

# ─── Violation Types ──────────────────────────────────────────────────────────
VIOLATION_TYPES = [
    "helmet_non_compliance",
    "seatbelt_non_compliance",
    "triple_riding",
    "wrong_side_driving",
    "stop_line_violation",
    "red_light_violation",
    "illegal_parking",
    "no_violation",
]

# Human-readable labels for display
VIOLATION_LABELS = {
    "helmet_non_compliance":   "Helmet Non-Compliance",
    "seatbelt_non_compliance": "Seatbelt Non-Compliance",
    "triple_riding":           "Triple Riding",
    "wrong_side_driving":      "Wrong-Side Driving",
    "stop_line_violation":     "Stop-Line Violation",
    "red_light_violation":     "Red-Light Violation",
    "illegal_parking":         "Illegal Parking",
    "no_violation":            "No Violation",
}

# Severity levels
VIOLATION_SEVERITY = {
    "helmet_non_compliance":   "HIGH",
    "seatbelt_non_compliance": "MEDIUM",
    "triple_riding":           "HIGH",
    "wrong_side_driving":      "CRITICAL",
    "stop_line_violation":     "MEDIUM",
    "red_light_violation":     "HIGH",
    "illegal_parking":         "LOW",
    "no_violation":            "NONE",
}

# Bounding box colors per violation (BGR for OpenCV)
VIOLATION_COLORS = {
    "helmet_non_compliance":   (0, 0, 255),
    "seatbelt_non_compliance": (0, 140, 255),
    "triple_riding":           (0, 0, 200),
    "wrong_side_driving":      (0, 0, 180),
    "stop_line_violation":     (0, 165, 255),
    "red_light_violation":     (0, 0, 255),
    "illegal_parking":         (255, 165, 0),
    "no_violation":            (0, 255, 0),
    "vehicle":                 (255, 255, 0),
    "person":                  (255, 0, 255),
    "license_plate":           (0, 255, 255),
}

# ─── Detection Thresholds ─────────────────────────────────────────────────────
DETECTION_CONFIDENCE_THRESHOLD = 0.40
NMS_IOU_THRESHOLD              = 0.45
PLATE_CONFIDENCE_THRESHOLD     = 0.35

# ─── Heuristic Violation Rules ───────────────────────────────────────────────
TRIPLE_RIDING_PERSON_THRESHOLD = 3
PARKING_ZONE_IOU_THRESHOLD     = 0.30
WRONG_SIDE_LANE_RATIO          = 0.45
STOP_LINE_Y_RATIO              = 0.85
TRAFFIC_LIGHT_ROI_RATIO        = (0.0, 0.0, 0.15, 0.25)

# ─── Preprocessing ────────────────────────────────────────────────────────────
CLAHE_CLIP_LIMIT    = 2.0
CLAHE_TILE_GRID     = (8, 8)
DENOISE_H           = 10
DENOISE_TEMPLATE_WS = 7
DENOISE_SEARCH_WS   = 21

# ─── Output ───────────────────────────────────────────────────────────────────
ANNOTATION_FONT_SCALE  = 0.55
ANNOTATION_THICKNESS   = 2
ANNOTATION_BOX_PADDING = 5
OUTPUT_IMAGE_QUALITY   = 95

# ─── OCR ──────────────────────────────────────────────────────────────────────
OCR_LANGUAGES       = ["en"]
OCR_MIN_TEXT_LENGTH = 4
OCR_PLATE_PATTERN   = r"[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}"
