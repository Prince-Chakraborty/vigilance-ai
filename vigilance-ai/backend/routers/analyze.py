"""
VigilanceAI — Analyze Router
POST /api/v1/analyze — accepts image upload, queues job, returns job_id immediately
GET  /api/v1/analyze/status/{job_id} — poll for result
"""
import sys
import json
import gc
import uuid
import threading
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
from db.database import get_db, ViolationRecord, SessionLocal
from models.schemas import AnalyzeResponse

router = APIRouter()

# In-memory job store
_jobs: dict = {}

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

def _run_inference(job_id: str, img_bgr, camera_id: str, location: str, has_stop_line: bool):
    try:
        _jobs[job_id]["status"] = "processing"
        pipeline = get_pipeline()
        pipeline.camera_id = camera_id
        pipeline.location  = location

        evidence = pipeline.analyze_from_numpy(img_bgr, has_stop_line=has_stop_line)
        paths    = pipeline.evidence.save_evidence(evidence)
        evidence["saved_paths"] = paths
        meta = evidence["metadata"]

        db: Session = SessionLocal()
        try:
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
        finally:
            db.close()

        api_resp = pipeline.to_api_response(evidence)
        gc.collect()

        _jobs[job_id]["status"] = "done"
        _jobs[job_id]["result"] = {
            "success"             : True,
            "incident_id"         : meta["incident_id"],
            "violation_count"     : meta["violation_count"],
            "annotated_image_b64" : api_resp["annotated_image_b64"],
            "metadata"            : meta,
        }
    except Exception as e:
        _jobs[job_id]["status"] = "error"
        _jobs[job_id]["error"]  = str(e)

@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    camera_id: str = Form(default="CAM-001"),
    location: str = Form(default="Bengaluru, Karnataka"),
    has_stop_line: bool = Form(default=False),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()
    pil_img  = Image.open(io.BytesIO(contents)).convert("RGB")
    img_np   = np.array(pil_img)
    img_bgr  = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "queued", "result": None, "error": None}

    thread = threading.Thread(
        target=_run_inference,
        args=(job_id, img_bgr, camera_id, location, has_stop_line),
        daemon=True,
    )
    thread.start()

    return {"job_id": job_id, "status": "queued"}

@router.get("/analyze/status/{job_id}")
def get_job_status(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] == "done":
        return {"status": "done", "result": job["result"]}
    if job["status"] == "error":
        raise HTTPException(status_code=500, detail=job["error"])
    return {"status": job["status"]}
