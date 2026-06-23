cat > /Users/princechakraborty/vigilance-ai/vigilance-ai/README.md << 'EOF'
# VigilanceAI — Automated Traffic Violation Detection System
**Flipkart Gridlock 2.0 | Round 2 | Theme 3: Traffic Violation Detection**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-brightgreen)](https://vigilance-ai-ochre.vercel.app)
[![Backend](https://img.shields.io/badge/Backend-Render-blue)](https://vigilance-ai-backend.onrender.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)]()

---

## Problem Statement

Bengaluru processes **7.2 million+ vehicles daily** across 1,200+ traffic junctions. Manual inspection of CCTV footage is:
- Labor-intensive and unscalable
- Inconsistent across shifts and operators
- Unable to process real-time feeds at scale
- Prone to human error in enforcement

VigilanceAI replaces manual monitoring with an automated, AI-powered pipeline that detects, classifies, and enforces traffic violations in real time.

---

## Live Demo

| Component | URL |
|-----------|-----|
| 🌐 Frontend Dashboard | https://vigilance-ai-ochre.vercel.app |
| ⚙️ Backend API | https://vigilance-ai-backend.onrender.com |
| 📖 API Docs | https://vigilance-ai-backend.onrender.com/docs |

> **Note:** Backend runs on Render free tier (512MB RAM). Full YOLO pipeline runs locally and on production hardware. Live demo uses OpenCV-based detection engine.

---

## Architecture Traffic Camera Feed

│

▼

┌─────────────────────────────────────────┐

│           CV Pipeline (Core)            │

│  CLAHE Preprocessing → YOLOv8 Detection │

│  → Violation Classifier → EasyOCR      │

│  → Evidence Generator                   │

└─────────────────────────────────────────┘

│

▼

┌─────────────────────────────────────────┐

│         FastAPI Backend                 │

│  /analyze → /violations → /challans    │

│  SQLAlchemy ORM → SQLite DB            │

└─────────────────────────────────────────┘

│

▼

┌─────────────────────────────────────────┐

│         React Dashboard                 │

│  Real-time Stats → Violation DB        │

│  Challan Management → Image Analysis  │

└─────────────────────────────────────────┘---

## Violations Detected

| Violation | Severity | Fine (₹) |
|-----------|----------|----------|
| Wrong-Side Driving | CRITICAL | 5,000 |
| Red-Light Jump | HIGH | 2,000 |
| Overspeeding | HIGH | 1,500 |
| No Helmet | MEDIUM | 1,000 |
| Stop-Line Violation | MEDIUM | 500 |
| Illegal Parking | LOW | 300 |
| Triple Riding | HIGH | 1,500 |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Object Detection | YOLOv8n (Ultralytics) |
| Preprocessing | OpenCV + CLAHE |
| OCR | EasyOCR (Indian plates) |
| Backend | FastAPI + SQLAlchemy + SQLite |
| Frontend | React + Recharts |
| Deployment | Vercel (Frontend) + Render (Backend) |

---

## Project Structure vigilance-ai/

├── core/                    # CV pipeline

│   ├── pipeline.py          # Main detection pipeline

│   ├── detector.py          # YOLOv8 wrapper

│   ├── violation_classifier.py

│   ├── ocr_engine.py        # EasyOCR integration

│   └── evidence.py          # Annotated image generator

├── backend/

│   ├── main.py              # FastAPI app

│   ├── routers/

│   │   ├── analyze.py       # Image analysis endpoint

│   │   ├── violations.py    # Violation CRUD

│   │   ├── challan.py       # Challan management

│   │   └── stats.py         # Analytics

│   ├── db/

│   │   └── database.py      # SQLAlchemy models

│   └── utils/

│       └── seed.py          # Demo data seeder

└── frontend/

├── src/

│   ├── pages/

│   │   ├── Dashboard.js

│   │   ├── Analyze.js

│   │   ├── Violations.js

│   │   └── Challans.js

│   └── api.js

└── package.json

---

## Instructions to Run Locally

### Prerequisites
- Python 3.9+
- Node.js 16+

### 1. Clone Repository
```bash
git clone https://github.com/Prince-Chakraborty/vigilance-ai.git
cd vigilance-ai/vigilance-ai
```

### 2. Install Backend Dependencies
```bash
cd backend
pip3 install ultralytics easyocr opencv-python-headless Pillow numpy fastapi uvicorn python-multipart sqlalchemy aiofiles
```

### 3. Seed Database
```bash
python3 utils/seed.py
```

### 4. Start Backend
```bash
python3 -m uvicorn main:app --reload --port 8000
```

### 5. Start Frontend
```bash
cd ../frontend
npm install
npm start
```

### 6. Open Dashboard
http://localhost:3000

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/analyze | Upload image for violation detection |
| GET | /api/v1/violations | List all violation records |
| GET | /api/v1/stats | Dashboard analytics |
| GET | /api/v1/stats/daily | Daily trend data |
| GET | /api/v1/stats/cameras | Per-camera stats |
| POST | /api/v1/challan/{id} | Issue automated challan |
| PATCH | /api/v1/challan/{id}/status | Update challan status |
| GET | /api/v1/challans/summary | Fine collection summary |

---

## Performance Metrics

- **Detection Model:** YOLOv8n — mAP@0.5: 37.3 (Ultralytics benchmark)
- **Inference Speed:** ~20 FPS on CPU (local), 2-3s on Render free tier
- **Confidence Threshold:** 40%
- **Test Coverage:** 29 unit tests passing
- **Supported Formats:** JPG, PNG, WEBP

---

## Scalability

For production deployment:
1. **Containerize** backend with Docker
2. **Queue inference** with Celery + Redis for concurrent camera feeds
3. **Replace SQLite** with PostgreSQL for multi-node deployment
4. **GPU inference** reduces latency from 2s to <100ms per frame
5. **Horizontal scaling** via Kubernetes for city-wide deployment

---

## Known Limitations

- Emergency vehicles not distinguished from regular traffic
- Heavily obstructed license plates reduce OCR accuracy
- Fog/night conditions reduce detection confidence
- Free tier hosting limits inference to 2-3s per image

---

## Team

**Prince Chakraborty** — IEM Kolkata
Flipkart Gridlock 2.0 — Round 2 | Theme 3: Traffic Violation Detection