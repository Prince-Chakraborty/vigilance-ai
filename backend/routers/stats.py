"""
VigilanceAI — Statistics Router
GET endpoints for analytics and reporting.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from db.database import get_db, ViolationRecord, ChallanRecord
from models.schemas import StatsResponse, ViolationRecordOut

router = APIRouter()


@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """
    Returns full analytics summary for the dashboard.
    """
    total_violations = db.query(ViolationRecord).count()
    total_challans   = db.query(ChallanRecord).count()

    # Violations by type
    by_type_rows = db.query(
        ViolationRecord.violation_type,
        func.count(ViolationRecord.id).label("count")
    ).group_by(ViolationRecord.violation_type).all()
    violations_by_type = {row.violation_type: row.count for row in by_type_rows}

    # Violations by severity
    by_severity_rows = db.query(
        ViolationRecord.severity,
        func.count(ViolationRecord.id).label("count")
    ).group_by(ViolationRecord.severity).all()
    violations_by_severity = {row.severity: row.count for row in by_severity_rows}

    # Top locations
    top_location_rows = db.query(
        ViolationRecord.location,
        func.count(ViolationRecord.id).label("count")
    ).group_by(ViolationRecord.location).order_by(
        desc(func.count(ViolationRecord.id))
    ).limit(5).all()
    top_locations = [
        {"location": row.location, "count": row.count}
        for row in top_location_rows
    ]

    # Recent 10 violations
    recent = db.query(ViolationRecord).order_by(
        desc(ViolationRecord.timestamp)
    ).limit(10).all()

    return StatsResponse(
        total_violations       = total_violations,
        total_challans         = total_challans,
        violations_by_type     = violations_by_type,
        violations_by_severity = violations_by_severity,
        top_locations          = top_locations,
        recent_violations      = [ViolationRecordOut.from_orm(r) for r in recent],
    )


@router.get("/stats/daily")
def get_daily_stats(db: Session = Depends(get_db)):
    """
    Returns violation counts grouped by date for trend charts.
    """
    rows = db.query(
        func.date(ViolationRecord.timestamp).label("date"),
        func.count(ViolationRecord.id).label("count")
    ).group_by(
        func.date(ViolationRecord.timestamp)
    ).order_by("date").all()

    return {
        "daily": [
            {"date": str(row.date), "count": row.count}
            for row in rows
        ]
    }


@router.get("/stats/cameras")
def get_camera_stats(db: Session = Depends(get_db)):
    """
    Returns violation counts per camera.
    """
    rows = db.query(
        ViolationRecord.camera_id,
        func.count(ViolationRecord.id).label("count")
    ).group_by(ViolationRecord.camera_id).order_by(
        desc(func.count(ViolationRecord.id))
    ).all()

    return {
        "cameras": [
            {"camera_id": row.camera_id, "count": row.count}
            for row in rows
        ]
    }
