# VigilanceAI — Automated Traffic Violation Detection System

Flipkart Gridlock 2.0 — Round 2 Prototype

## Problem Statement
Manual inspection of traffic camera footage is labor-intensive, inconsistent, and unscalable. VigilanceAI automates detection, classification, and enforcement of traffic violations using computer vision.

## Solution
An end-to-end AI system that detects vehicles and riders using YOLOv8, classifies 7 types of traffic violations, reads license plates using EasyOCR, generates annotated evidence images, issues automated challans, and displays real-time analytics on a command dashboard.

## Violations Detected
- Helmet Non-Compliance (HIGH)
- Seatbelt Non-Compliance (MEDIUM)
- Triple Riding (HIGH)
- Wrong-Side Driving (CRITICAL)
- Stop-Line Violation (MEDIUM)
- Red-Light Violation (HIGH)
- Illegal Parking (LOW)

## Tech Stack
- CV Engine: YOLOv8 + OpenCV + CLAHE preprocessing
- OCR: EasyOCR optimized for Indian number plates
- Backend: FastAPI + SQLAlchemy + SQLite
- Frontend: React + Recharts
- Testing: pytest with 29 passing tests

## Instructions to Run

### 1. Install dependencies
pip3 install ultralytics easyocr opencv-python-headless Pillow numpy fastapi uvicorn python-multipart sqlalchemy

### 2. Seed the database
cd backend && python3 utils/seed.py

### 3. Start Backend
cd backend && python3 -m uvicorn main:app --reload --port 8000

### 4. Start Frontend
cd frontend && npm install && npm start

### 5. Open Dashboard
http://localhost:3000

### 6. API Docs
http://localhost:8000/docs

## API Endpoints
- POST /api/v1/analyze — Upload image for violation detection
- GET  /api/v1/violations — List all violation records
- GET  /api/v1/stats — Dashboard analytics and trends
- POST /api/v1/challan/{id} — Issue automated challan
- GET  /api/v1/challans/summary — Fine collection summary

## Performance
- Detection confidence threshold: 40%
- Supports JPG, PNG, WEBP input formats
- 29 unit tests passing
- Evidence stored as annotated JPEG + JSON metadata

## Team
Prince Chakraborty — IEM Kolkata
Flipkart Gridlock 2.0 — Round 2 Prototype
