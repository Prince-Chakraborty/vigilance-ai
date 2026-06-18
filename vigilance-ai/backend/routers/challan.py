"""
VigilanceAI — Challan Router
Generates automated traffic challans (tickets) for violations.
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from db.database import get_db, ViolationRecord, ChallanRecord
from models.schemas import ChallanOut

router = APIRouter()

# Fine amounts per violation type (INR)
FINE_AMOUNTS = {
    "helmet_non_compliance":   1000.0,
    "seatbelt_non_compliance": 1000.0,
    "triple_riding":           2000.0,
    "wrong_side_driving":      5000.0,
    "stop_line_violation":     1000.0,
    "red_light_violation":     5000.0,
    "illegal_parking":         500.0,
    "no_violation":            0.0,
}


@router.post("/challan/{incident_id}", response_model=ChallanOut)
def issue_challan(incident_id: str, db: Session = Depends(get_db)):
    """
    Issue a challan for a recorded violation by incident ID.
    """
    record = db.query(ViolationRecord).filter(
        ViolationRecord.incident_id == incident_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Violation record not found")

    if record.challan_issued:
        raise HTTPException(status_code=400, detail="Challan already issued for this violation")

    if not record.license_plate:
        raise HTTPException(status_code=400, detail="License plate required to issue challan")

    challan_id  = f"CHL-{str(uuid.uuid4())[:8].upper()}"
    fine_amount = FINE_AMOUNTS.get(record.violation_type, 1000.0)

    challan = ChallanRecord(
        challan_id      = challan_id,
        incident_id     = incident_id,
        license_plate   = record.license_plate,
        violation_type  = record.violation_type,
        violation_label = record.violation_label,
        severity        = record.severity,
        fine_amount     = fine_amount,
        location        = record.location,
        timestamp       = datetime.utcnow(),
        camera_id       = record.camera_id,
        status          = "ISSUED",
    )

    db.add(challan)
    record.challan_issued = True
    db.commit()
    db.refresh(challan)

    return challan


@router.get("/challans", response_model=List[ChallanOut])
def get_challans(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Fetch all issued challans.
    """
    return db.query(ChallanRecord).order_by(
        desc(ChallanRecord.timestamp)
    ).offset(skip).limit(limit).all()


@router.get("/challan/{challan_id}", response_model=ChallanOut)
def get_challan(challan_id: str, db: Session = Depends(get_db)):
    """
    Fetch a single challan by ID.
    """
    challan = db.query(ChallanRecord).filter(
        ChallanRecord.challan_id == challan_id
    ).first()
    if not challan:
        raise HTTPException(status_code=404, detail="Challan not found")
    return challan


@router.patch("/challan/{challan_id}/status")
def update_challan_status(
    challan_id: str,
    status: str,
    db: Session = Depends(get_db)
):
    """
    Update challan status: ISSUED → PAID or CANCELLED.
    """
    valid_statuses = ["ISSUED", "PAID", "CANCELLED"]
    if status.upper() not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    challan = db.query(ChallanRecord).filter(
        ChallanRecord.challan_id == challan_id
    ).first()
    if not challan:
        raise HTTPException(status_code=404, detail="Challan not found")

    challan.status = status.upper()
    db.commit()
    return {"success": True, "challan_id": challan_id, "status": challan.status}


@router.get("/challans/summary")
def challan_summary(db: Session = Depends(get_db)):
    """
    Returns total fines collected and pending.
    """
    all_challans = db.query(ChallanRecord).all()
    total_issued    = sum(c.fine_amount for c in all_challans)
    total_collected = sum(c.fine_amount for c in all_challans if c.status == "PAID")
    total_pending   = sum(c.fine_amount for c in all_challans if c.status == "ISSUED")

    return {
        "total_challans":   len(all_challans),
        "total_issued_inr": total_issued,
        "total_collected_inr": total_collected,
        "total_pending_inr":   total_pending,
    }
