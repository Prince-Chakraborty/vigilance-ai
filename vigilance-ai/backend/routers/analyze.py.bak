"""
VigilanceAI — Analyze Router
POST /api/v1/analyze — accepts image upload, runs full pipeline,
saves to DB, returns annotated image + metadata.
"""

import sys
import json
import gc
import numpy as np
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from PIL import Image
import io
import cv2

CORE_PATH = Path(__file__).parent.parent.parent / "core"
sys.path.insert(0, str(CORE_PATH))

from pipeline import VigilancePipeline
from db.database import get_db, ViolationRecord
from models.schemas import AnalyzeResponse

router = APIRouter()

_pipeline = None

def get_pipeline() -> VigilancePipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = VigilancePipeline(
            yolo_model="yolov8n.pt",
            enable_ocr=False,
            output_dir="backend/static/evidence",
        )
    return _pipeline


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_image(
    file: UploadFile = File(...),
    camera_id: str = Form(default="CAM-001"),
    location: str = Form(default="Bengaluru, Karnataka"),
    has_stop_line: bool = Form(default=False),
    db: Session = Depends(get_db),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()
    pil_img  = Image.open(io.BytesIO(contents)).convert("RGB")
    img_np   = np.array(pil_img)
    img_bgr  = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    pipeline = get_pipeline()
    pipeline.camera_id = camera_id
    pipeline.location  = location

    evidence = pipeline.analyze_from_numpy(img_bgr, has_stop_line=has_stop_line)
    paths    = pipeline.evidence.save_evidence(evidence)
    evidence["saved_paths"] = paths
    meta = evidence["metadata"]

    for v in meta["violations"]:
        record = ViolationRecord(
            incident_id     = f"{meta['incident_id']}-{v['violation_type']}",
            timestamp       = datetime.fromisoformat(meta["timestamp"]),
            camera_id       = meta["camera_id"],
            location        = meta["location"],
            violation_type  = v["violation_type"],
            violation_label = v["violation_label"],
            severity        = v["severity"],
            confidence      = v["confidence"],
            license_plate   = v.get("license_plate"),
            notes           = v.get("notes"),
            bbox_x1         = v["bbox"]["x1"],
            bbox_y1         = v["bbox"]["y1"],
            bbox_x2         = v["bbox"]["x2"],
            bbox_y2         = v["bbox"]["y2"],
            annotated_image = paths.get("annotated_image"),
            metadata_json   = json.dumps(meta),
            challan_issued  = False,
        )
        db.add(record)

    db.commit()

    api_resp = pipeline.to_api_response(evidence)

    gc.collect()

    return AnalyzeResponse(
        success             = True,
        incident_id         = meta["incident_id"],
        violation_count     = meta["violation_count"],
        annotated_image_b64 = api_resp["annotated_image_b64"],
        metadata            = meta,
    )
