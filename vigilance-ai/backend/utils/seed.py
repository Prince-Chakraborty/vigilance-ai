"""
VigilanceAI — Seed Data
Populates DB with sample violation records for dashboard demo.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))

from db.database import init_db, SessionLocal, ViolationRecord, ChallanRecord

VIOLATION_TYPES = [
    ("helmet_non_compliance",   "Helmet Non-Compliance",   "HIGH",     1000.0),
    ("seatbelt_non_compliance", "Seatbelt Non-Compliance", "MEDIUM",   1000.0),
    ("triple_riding",           "Triple Riding",           "HIGH",     2000.0),
    ("wrong_side_driving",      "Wrong-Side Driving",      "CRITICAL", 5000.0),
    ("stop_line_violation",     "Stop-Line Violation",     "MEDIUM",   1000.0),
    ("red_light_violation",     "Red-Light Violation",     "HIGH",     5000.0),
    ("illegal_parking",         "Illegal Parking",         "LOW",      500.0),
]

CAMERAS = ["CAM-001", "CAM-002", "CAM-003", "CAM-004", "CAM-005"]

LOCATIONS = [
    "MG Road, Bengaluru",
    "Silk Board Junction, Bengaluru",
    "Hebbal Flyover, Bengaluru",
    "Whitefield Main Road, Bengaluru",
    "Koramangala 5th Block, Bengaluru",
]

PLATES = [
    "KA05MJ7890", "KA01AB1234", "KA03CD5678",
    "KA04EF9012", "KA09GH3456", "KA51IJ7890",
    "MH12KL2345", "TN07MN6789", "DL08OP0123",
]


def seed():
    init_db()
    db = SessionLocal()

    # Clear existing seed data
    db.query(ViolationRecord).delete()
    db.query(ChallanRecord).delete()
    db.commit()

    print("[Seed] Inserting sample violation records...")

    challan_counter = 0
    for i in range(60):
        vtype, vlabel, severity, fine = random.choice(VIOLATION_TYPES)
        plate    = random.choice(PLATES) if random.random() > 0.3 else None
        camera   = random.choice(CAMERAS)
        location = random.choice(LOCATIONS)
        ts       = datetime.utcnow() - timedelta(
            days=random.randint(0, 14),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        incident_id = f"SEED-{i+1:04d}-{vtype[:4].upper()}"
        challan_issued = plate is not None and random.random() > 0.5

        record = ViolationRecord(
            incident_id     = incident_id,
            timestamp       = ts,
            camera_id       = camera,
            location        = location,
            violation_type  = vtype,
            violation_label = vlabel,
            severity        = severity,
            confidence      = round(random.uniform(0.65, 0.97), 3),
            license_plate   = plate,
            notes           = f"Auto-detected by VigilanceAI at {location}",
            bbox_x1         = random.uniform(50, 200),
            bbox_y1         = random.uniform(50, 150),
            bbox_x2         = random.uniform(300, 500),
            bbox_y2         = random.uniform(250, 400),
            challan_issued  = challan_issued,
        )
        db.add(record)

        if challan_issued and plate:
            challan_counter += 1
            challan = ChallanRecord(
                challan_id      = f"CHL-SEED-{challan_counter:04d}",
                incident_id     = incident_id,
                license_plate   = plate,
                violation_type  = vtype,
                violation_label = vlabel,
                severity        = severity,
                fine_amount     = fine,
                location        = location,
                timestamp       = ts,
                camera_id       = camera,
                status          = random.choice(["ISSUED", "PAID", "ISSUED", "ISSUED"]),
            )
            db.add(challan)

    db.commit()
    db.close()
    print(f"[Seed] Done — 60 violations, {challan_counter} challans inserted ✓")


if __name__ == "__main__":
    seed()
