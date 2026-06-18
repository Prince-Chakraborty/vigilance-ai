"""
VigilanceAI — FastAPI Backend
"""

import sys
import os
from pathlib import Path

CORE_PATH = Path(__file__).resolve().parent.parent / "vigilance-ai" / "core"
sys.path.insert(0, str(CORE_PATH))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers import analyze, violations, stats, challan

app = FastAPI(
    title="VigilanceAI API",
    description="Automated Traffic Violation Detection System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/evidence", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(analyze.router,    prefix="/api/v1", tags=["Analysis"])
app.include_router(violations.router, prefix="/api/v1", tags=["Violations"])
app.include_router(stats.router,      prefix="/api/v1", tags=["Statistics"])
app.include_router(challan.router,    prefix="/api/v1", tags=["Challan"])


@app.get("/")
def root():
    return {
        "system": "VigilanceAI",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
