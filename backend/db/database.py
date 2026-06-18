"""
VigilanceAI — Database Setup
SQLite for local dev, easily swappable to PostgreSQL for production.
"""

from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vigilance.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ─── Models ───────────────────────────────────────────────────────────────────

class ViolationRecord(Base):
    __tablename__ = "violations"

    id              = Column(Integer, primary_key=True, index=True)
    incident_id     = Column(String, unique=True, index=True)
    timestamp       = Column(DateTime, default=datetime.utcnow)
    camera_id       = Column(String, default="CAM-001")
    location        = Column(String, default="Bengaluru, Karnataka")
    violation_type  = Column(String, index=True)
    violation_label = Column(String)
    severity        = Column(String)
    confidence      = Column(Float)
    license_plate   = Column(String, nullable=True)
    notes           = Column(Text, nullable=True)
    bbox_x1         = Column(Float)
    bbox_y1         = Column(Float)
    bbox_x2         = Column(Float)
    bbox_y2         = Column(Float)
    annotated_image = Column(String, nullable=True)
    metadata_json   = Column(Text, nullable=True)
    challan_issued  = Column(Boolean, default=False)


class ChallanRecord(Base):
    __tablename__ = "challans"

    id             = Column(Integer, primary_key=True, index=True)
    challan_id     = Column(String, unique=True, index=True)
    incident_id    = Column(String, index=True)
    license_plate  = Column(String)
    violation_type = Column(String)
    violation_label= Column(String)
    severity       = Column(String)
    fine_amount    = Column(Float)
    location       = Column(String)
    timestamp      = Column(DateTime, default=datetime.utcnow)
    camera_id      = Column(String)
    status         = Column(String, default="ISSUED")
    pdf_path       = Column(String, nullable=True)


# ─── Init DB ──────────────────────────────────────────────────────────────────

def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
