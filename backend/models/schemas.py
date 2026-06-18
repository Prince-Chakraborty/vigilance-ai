"""
VigilanceAI — Pydantic Schemas
Request/Response models for API endpoints.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class BBoxSchema(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class ViolationSchema(BaseModel):
    violation_type:  str
    violation_label: str
    severity:        str
    confidence:      float
    license_plate:   Optional[str] = None
    notes:           Optional[str] = None
    bbox:            BBoxSchema


class AnalysisMetadata(BaseModel):
    incident_id:      str
    timestamp:        str
    camera_id:        str
    location:         str
    source_file:      str
    frame_size:       List[int]
    total_vehicles:   int
    total_persons:    int
    violations:       List[ViolationSchema]
    violation_count:  int
    red_light_active: bool


class AnalyzeResponse(BaseModel):
    success:             bool
    incident_id:         str
    violation_count:     int
    annotated_image_b64: str
    metadata:            AnalysisMetadata


class ViolationRecordOut(BaseModel):
    id:              int
    incident_id:     str
    timestamp:       datetime
    camera_id:       str
    location:        str
    violation_type:  str
    violation_label: str
    severity:        str
    confidence:      float
    license_plate:   Optional[str]
    notes:           Optional[str]
    challan_issued:  bool

    class Config:
        from_attributes = True


class ChallanOut(BaseModel):
    challan_id:      str
    incident_id:     str
    license_plate:   str
    violation_type:  str
    violation_label: str
    severity:        str
    fine_amount:     float
    location:        str
    timestamp:       datetime
    camera_id:       str
    status:          str

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    total_violations:    int
    total_challans:      int
    violations_by_type:  dict
    violations_by_severity: dict
    top_locations:       List[dict]
    recent_violations:   List[ViolationRecordOut]
