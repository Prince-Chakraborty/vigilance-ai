"""
VigilanceAI — Core Test Suite
Run from vigilance-ai/ directory: python -m pytest core/tests/ -v
"""

import sys
import numpy as np
import cv2
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from preprocessing.enhancer import (
    apply_clahe, sharpen, gamma_correction,
    detect_low_light, detect_blur, preprocess, normalize
)
from detection.detector import BBox, FrameAnalysis
from output.annotator import Annotator, EvidenceGenerator


def make_bgr(h=480, w=640, brightness=128) -> np.ndarray:
    img = np.full((h, w, 3), brightness, dtype=np.uint8)
    cv2.rectangle(img, (100, 100), (300, 300), (200, 100, 50), -1)
    cv2.circle(img, (400, 200), 80, (50, 200, 150), -1)
    return img


def make_dark_bgr(h=480, w=640) -> np.ndarray:
    return make_bgr(h, w, brightness=30)


class TestPreprocessing:

    def test_clahe_output_shape(self):
        img = make_bgr()
        out = apply_clahe(img)
        assert out.shape == img.shape
        assert out.dtype == np.uint8

    def test_clahe_changes_pixels(self):
        img = make_bgr(brightness=100)
        out = apply_clahe(img)
        assert not np.array_equal(img, out)

    def test_gamma_brightens(self):
        img = make_dark_bgr()
        out = gamma_correction(img, gamma=1.5)
        assert out.mean() > img.mean()

    def test_detect_low_light_dark(self):
        assert detect_low_light(make_dark_bgr(), threshold=60) is True

    def test_detect_low_light_bright(self):
        assert detect_low_light(make_bgr(brightness=180), threshold=60) is False

    def test_detect_blur_blurry(self):
        img = make_bgr()
        blurry = cv2.GaussianBlur(img, (21, 21), 0)
        assert detect_blur(blurry, threshold=80.0) is True

    def test_detect_blur_sharp(self):
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        img[::2, ::2] = 255
        assert detect_blur(img, threshold=80.0) is False

    def test_sharpen_shape(self):
        img = make_bgr()
        assert sharpen(img).shape == img.shape

    def test_normalize_range(self):
        img = make_bgr(brightness=50)
        out = normalize(img)
        assert int(out.max()) == 255
        assert int(out.min()) == 0

    def test_preprocess_pipeline(self):
        img = make_dark_bgr()
        out = preprocess(img, enable_denoise=False)
        assert out.shape == img.shape
        assert out.dtype == np.uint8

    def test_preprocess_bright_image(self):
        img = make_bgr(brightness=200)
        out = preprocess(img, enable_denoise=False)
        assert out.shape == img.shape


class TestBBox:

    def test_centroid(self):
        b = BBox(0, 0, 100, 100)
        assert b.cx == 50.0
        assert b.cy == 50.0

    def test_area(self):
        assert BBox(0, 0, 100, 200).area == 20000.0

    def test_iou_identical(self):
        b = BBox(0, 0, 100, 100)
        assert abs(b.iou(b) - 1.0) < 1e-6

    def test_iou_no_overlap(self):
        assert BBox(0, 0, 50, 50).iou(BBox(100, 100, 200, 200)) == 0.0

    def test_iou_partial(self):
        iou = BBox(0, 0, 100, 100).iou(BBox(50, 50, 150, 150))
        assert 0 < iou < 1

    def test_contains_center_true(self):
        assert BBox(0, 0, 200, 200).contains_center(BBox(80, 80, 120, 120)) is True

    def test_contains_center_false(self):
        assert BBox(0, 0, 50, 50).contains_center(BBox(200, 200, 300, 300)) is False


class TestAnnotator:

    def test_annotate_no_violations(self):
        img = make_bgr()
        analysis = FrameAnalysis(
            detections=[], violations=[],
            frame_width=640, frame_height=480
        )
        out = Annotator().annotate(img, analysis)
        assert out.shape == img.shape

    def test_annotate_no_mutation(self):
        img = make_bgr()
        original = img.copy()
        analysis = FrameAnalysis(
            detections=[], violations=[],
            frame_width=640, frame_height=480
        )
        Annotator().annotate(img, analysis)
        assert np.array_equal(img, original)

    def test_annotate_returns_uint8(self):
        img = make_bgr()
        analysis = FrameAnalysis(
            detections=[], violations=[],
            frame_width=640, frame_height=480
        )
        assert Annotator().annotate(img, analysis).dtype == np.uint8


class TestEvidenceGenerator:

    def test_generate_keys(self, tmp_path):
        gen = EvidenceGenerator(output_dir=str(tmp_path))
        img = make_bgr()
        analysis = FrameAnalysis(detections=[], violations=[], frame_width=640, frame_height=480)
        ev = gen.generate(img, img, analysis)
        assert "incident_id" in ev
        assert "annotated_img" in ev
        assert "metadata" in ev

    def test_save_creates_files(self, tmp_path):
        gen = EvidenceGenerator(output_dir=str(tmp_path))
        img = make_bgr()
        analysis = FrameAnalysis(detections=[], violations=[], frame_width=640, frame_height=480)
        ev = gen.generate(img, img, analysis)
        paths = gen.save_evidence(ev)
        assert Path(paths["annotated_image"]).exists()
        assert Path(paths["metadata_json"]).exists()

    def test_api_response_has_b64(self, tmp_path):
        gen = EvidenceGenerator(output_dir=str(tmp_path))
        img = make_bgr()
        analysis = FrameAnalysis(detections=[], violations=[], frame_width=640, frame_height=480)
        ev = gen.generate(img, img, analysis)
        resp = gen.to_api_response(ev)
        assert "annotated_image_b64" in resp
        assert len(resp["annotated_image_b64"]) > 100

    def test_metadata_keys(self, tmp_path):
        gen = EvidenceGenerator(output_dir=str(tmp_path))
        img = make_bgr()
        analysis = FrameAnalysis(detections=[], violations=[], frame_width=640, frame_height=480)
        ev = gen.generate(img, img, analysis)
        for key in ["incident_id", "timestamp", "camera_id", "location", "violations", "violation_count"]:
            assert key in ev["metadata"]


class TestConfig:

    def test_violation_colors_complete(self):
        from config import VIOLATION_TYPES, VIOLATION_COLORS
        for vt in VIOLATION_TYPES:
            assert vt in VIOLATION_COLORS

    def test_violation_severity_complete(self):
        from config import VIOLATION_TYPES, VIOLATION_SEVERITY
        for vt in VIOLATION_TYPES:
            assert vt in VIOLATION_SEVERITY

    def test_violation_labels_complete(self):
        from config import VIOLATION_TYPES, VIOLATION_LABELS
        for vt in VIOLATION_TYPES:
            assert vt in VIOLATION_LABELS

    def test_thresholds_in_range(self):
        from config import DETECTION_CONFIDENCE_THRESHOLD, NMS_IOU_THRESHOLD
        assert 0 < DETECTION_CONFIDENCE_THRESHOLD < 1
        assert 0 < NMS_IOU_THRESHOLD < 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
