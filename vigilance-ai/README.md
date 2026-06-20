# VigilanceAI — Automated Traffic Violation Detection System

> Flipkart Gridlock 2.0 — Round 2 Prototype Submission

## Live Links
- Dashboard: https://vigilance-ai-ochre.vercel.app
- API: https://vigilance-ai-backend.onrender.com
- API Docs: https://vigilance-ai-backend.onrender.com/docs

## Problem Statement
Manual inspection of traffic CCTV footage is labor-intensive, inconsistent, and unscalable. Bengaluru alone has thousands of cameras generating terabytes of footage daily — most violations go undetected.

## Solution
VigilanceAI is an end-to-end AI-powered traffic enforcement system that automatically detects vehicles and riders using YOLOv8, classifies 7 types of traffic violations, reads Indian license plates using EasyOCR, generates annotated evidence images, issues automated digital challans with fine amounts, and displays real-time analytics on a professional command dashboard.

## Violations Detected
- Helmet Non-Compliance — HIGH — Rs.1000
- Seatbelt Non-Compliance — MEDIUM — Rs.1000
- Triple Riding — HIGH — Rs.2000
- Wrong-Side Driving — CRITICAL — Rs.5000
- Stop-Line Violation — MEDIUM — Rs.1000
- Red-Light Violation — HIGH — Rs.5000
- Illegal Parking — LOW — Rs.500

## Tech Stack
- Object Detection: YOLOv8 (Ultralytics)
- Image Processing: OpenCV + CLAHE + Gamma Correction
- License Plate OCR: EasyOCR (Indian format)
- Backend API: FastAPI + SQLAlchemy
- Database: SQLite (dev) / PostgreSQL (prod)
- Frontend: React + Recharts
- Deployment: Render (backend) + Vercel (frontend)
- Testing: pytest (29 passing tests)

## Project Structure
- core/ — CV Engine (YOLOv8 + preprocessing + OCR + evidence)
- backend/ — FastAPI REST API (routers, models, DB, challan)
- frontend/ — React Dashboard (Dashboard, Analyze, Violations, Challans)
- run.py — Server entry point

## Instructions to Run

### Prerequisites
pip3 install ultralytics easyocr opencv-python-headless Pillow numpy fastapi uvicorn python-multipart sqlalchemy
cd frontend && npm install

### Start Backend
cd vigilance-ai && python3 run.py

### Seed Database
cd backend && python3 utils/seed.py

### Start Frontend
cd frontend && npm start

### Open Dashboard
http://localhost:3000

### API Documentation
http://localhost:8000/docs

## API Endpoints
- POST /api/v1/analyze — Upload image for violation detection
- GET  /api/v1/violations — List all violations with filters
- GET  /api/v1/stats — Dashboard analytics
- GET  /api/v1/stats/daily — Daily violation trends
- POST /api/v1/challan/{id} — Issue automated challan
- GET  /api/v1/challans/summary — Fine collection summary

## Key Features
- Real-time violation detection from traffic images
- Indian license plate recognition (KA, MH, TN, DL formats)
- Automated challan generation with fine amounts per Motor Vehicles Act
- Evidence package: annotated image + metadata JSON per incident
- Analytics dashboard with violation trends and hotspot mapping
- Searchable violation records by plate number, severity, camera
- 29 unit tests covering all core modules

## Team
Prince Chakraborty — B.Tech CSE, IEM Kolkata
Flipkart Gridlock 2.0 — Round 2 Prototype


## Performance Benchmarks
- Inference speed: 20 FPS on standard CPU (no GPU required)
- Average latency: 50ms per frame (6.3ms preprocessing + 43.7ms detection)
- Model: YOLOv8n (nano variant, optimized for edge/CCTV deployment)
- Suitable for real-time deployment on standard traffic camera infrastructure

## Known Limitations and Edge Case Handling
We believe in transparent reporting of system boundaries rather than overstating capabilities:

- Emergency vehicles (ambulance, police, fire) are not currently exempted from violation rules. Production deployment would require a dedicated emergency-vehicle classifier to suppress false positives.
- Severely obstructed or mud-covered license plates may fail OCR extraction. The system returns null in these cases rather than guessing, to avoid incorrect challans.
- Heavy rain or dense fog beyond moderate levels can reduce detection confidence below the 40% threshold, causing the system to skip uncertain detections rather than risk false violations.
- Current violation heuristics use geometric rules (lane position, bounding box overlap) rather than a fine-tuned violation-specific model. Fine-tuning YOLOv8 on a labeled Bengaluru violation dataset is the recommended next step for production accuracy.
- The system errs on the side of caution: when confidence is low or data is ambiguous, it does not flag a violation, prioritizing avoiding wrongful challans over catching every case.

## Future Improvements
- Fine-tune YOLOv8 on real Bengaluru CCTV footage with violation-specific labels
- Add emergency vehicle detection and exemption logic
- Integrate multi-frame temporal analysis for higher-confidence violations like red-light running
- Add WebSocket support for true real-time camera feed processing
