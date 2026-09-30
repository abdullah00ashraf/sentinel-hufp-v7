import os
# Must be at the very top to suppress TensorFlow warnings before anything else loads
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import uvicorn
import sys
import numpy as np

# Path Alignment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_manager import SentinelDB
from core.models import TacticalNode, IntelligenceMaster, MissionAudit

# FIX: Removed the relative dots (.) since this is now running from the root!
from weather_engine import WeatherEngine
from brain_proxy import BrainProxy

app = FastAPI(
    title="Sentinel V7.0 | Tactical Intelligence Hub",
    description="Lucknow Division Flood Intelligence & Neural Risk Assessment API",
    version="7.0.0"
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Initialize Engines
weather = WeatherEngine()
brain = BrainProxy()

def get_db():
    db = SentinelDB()
    session = db.get_session()
    try: yield session
    finally: session.close()

def serialize_data(obj):
    if isinstance(obj, (np.float64, np.floating)): return float(obj)
    if isinstance(obj, (np.int64, np.integer)): return int(obj)
    return obj

# --- 1. CORE TACTICAL ENDPOINTS ---

@app.get("/api/v7/tactical/top-threats", tags=["Tactical"])
async def top_threats(limit: int = 7, db: Session = Depends(get_db)):
    top_threats = db.query(TacticalNode, IntelligenceMaster).join(
        IntelligenceMaster, TacticalNode.id == IntelligenceMaster.node_id
    ).order_by(desc(IntelligenceMaster.risk_score)).limit(limit).all()
    
    # Added lat and lon to the returned dictionary for the frontend map tracking
    return [{"name": n.name, "risk": serialize_data(i.risk_score), "lat": n.lat, "lon": n.lon} for n, i in top_threats]

@app.get("/api/v7/analytics/division-summary", tags=["Analytics"])
async def get_division_stats(db: Session = Depends(get_db)):
    stats = db.query(
        func.avg(IntelligenceMaster.risk_score).label('avg_risk'),
        func.max(IntelligenceMaster.river_discharge).label('max_discharge')
    ).first()
    
    return {
        "average_division_risk": serialize_data(round(stats.avg_risk or 0, 4)),
        "peak_discharge_m3s": serialize_data(stats.max_discharge or 0),
        "total_indexed_records": 83986875 
    }

# --- 3. SYSTEM AUDIT & SEARCH ---

@app.get("/api/v7/system/audit-logs", tags=["System"])
async def get_mission_logs(limit: int = 5, db: Session = Depends(get_db)):
    logs = db.query(MissionAudit).order_by(desc(MissionAudit.timestamp)).limit(limit).all()
    return logs

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)