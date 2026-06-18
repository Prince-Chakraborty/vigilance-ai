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
