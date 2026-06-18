"""
VigilanceAI — Violations Router
GET endpoints to fetch violation records from DB.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from db.database import get_db, ViolationRecord
from models.schemas import ViolationRecordOut

router = APIRouter()


@router.get("/violations", response_model=List[ViolationRecordOut])
def get_violations(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=200),
    severity: Optional[str] = Query(default=None),
    violation_type: Optional[str] = Query(default=None),
    camera_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    """
    Fetch all violation records with optional filters.
    """
    query = db.query(ViolationRecord).order_by(desc(ViolationRecord.timestamp))

    if severity:
        query = query.filter(ViolationRecord.severity == severity.upper())
    if violation_type:
        query = query.filter(ViolationRecord.violation_type == violation_type)
    if camera_id:
        query = query.filter(ViolationRecord.camera_id == camera_id)

    return query.offset(skip).limit(limit).all()


@router.get("/violations/{incident_id}", response_model=ViolationRecordOut)
def get_violation(incident_id: str, db: Session = Depends(get_db)):
    """
    Fetch a single violation record by incident ID.
    """
    record = db.query(ViolationRecord).filter(
        ViolationRecord.incident_id == incident_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Violation not found")
    return record


@router.delete("/violations/{incident_id}")
def delete_violation(incident_id: str, db: Session = Depends(get_db)):
    """
    Delete a violation record by incident ID.
    """
    record = db.query(ViolationRecord).filter(
        ViolationRecord.incident_id == incident_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Violation not found")
    db.delete(record)
    db.commit()
    return {"success": True, "deleted": incident_id}


@router.get("/violations/search/{plate}")
def search_by_plate(plate: str, db: Session = Depends(get_db)):
    """
    Search violations by license plate number.
    """
    records = db.query(ViolationRecord).filter(
        ViolationRecord.license_plate.ilike(f"%{plate}%")
    ).order_by(desc(ViolationRecord.timestamp)).all()
    return {
        "plate": plate,
        "count": len(records),
        "violations": [ViolationRecordOut.from_orm(r) for r in records]
    }
