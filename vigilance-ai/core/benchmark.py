"""
VigilanceAI — Performance Benchmark
Measures inference speed (FPS) for the detection pipeline.
Run: python3 benchmark.py
"""

import time
import sys
import numpy as np
import cv2
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from detection.detector import ViolationDetector
from preprocessing.enhancer import preprocess


def make_test_frame(w=640, h=480):
    """Generate a synthetic traffic-like frame for benchmarking."""
    img = np.random.randint(60, 200, (h, w, 3), dtype=np.uint8)
    cv2.rectangle(img, (100, 200), (300, 350), (180, 180, 180), -1)
    cv2.rectangle(img, (350, 220), (500, 340), (160, 160, 160), -1)
    return img


def benchmark_detection(n_frames=30):
    print("=" * 55)
    print("  VigilanceAI — Inference Speed Benchmark")
    print("=" * 55)

    detector = ViolationDetector("yolov8n.pt")
    frame = make_test_frame()

    # Warmup (model JIT / first-call overhead)
    for _ in range(3):
        _ = detector.analyze(frame)

    # Benchmark preprocessing
    t0 = time.time()
    for _ in range(n_frames):
        _ = preprocess(frame, enable_denoise=False)
    preprocess_time = (time.time() - t0) / n_frames

    # Benchmark detection
    t0 = time.time()
    for _ in range(n_frames):
        _ = detector.analyze(frame)
    detection_time = (time.time() - t0) / n_frames

    total_time = preprocess_time + detection_time
    fps = 1 / total_time if total_time > 0 else 0

    print(f"\n  Frames tested        : {n_frames}")
    print(f"  Preprocessing avg    : {preprocess_time*1000:.1f} ms/frame")
    print(f"  YOLOv8n detection avg: {detection_time*1000:.1f} ms/frame")
    print(f"  Total pipeline avg   : {total_time*1000:.1f} ms/frame")
    print(f"  Throughput           : {fps:.1f} FPS")
    print(f"\n  Hardware: CPU (no GPU acceleration)")
    print(f"  Model: YOLOv8n (nano — optimized for edge deployment)")
    print("=" * 55)

    return {
        "fps": round(fps, 1),
        "avg_latency_ms": round(total_time * 1000, 1),
        "preprocessing_ms": round(preprocess_time * 1000, 1),
        "detection_ms": round(detection_time * 1000, 1),
    }


if __name__ == "__main__":
    benchmark_detection(n_frames=30)
