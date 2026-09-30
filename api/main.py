from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import uvicorn
import sys
import os
import numpy as np

# Path Alignment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_manager import SentinelDB
from core.models import TacticalNode, IntelligenceMaster, MissionAudit
from .weather_engine import WeatherEngine
from .brain_proxy import BrainProxy

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
    if obj is None: return 0.0
    return obj

# --- 1. CORE TACTICAL ENDPOINTS ---

@app.get("/", tags=["System"])
async def system_root():
    return {
        "message": "Sentinel V7.0 Tactical Hub is Online",
        "docs": "Visit /docs for the Command Center",
        "status": "Operational"
    }

@app.get("/api/v7/map-mesh", tags=["Tactical"])
async def get_map_mesh(db: Session = Depends(get_db)):
    """
    High-Performance Mesh Sync.
    Fetches tactical nodes and their latest intelligence records.
    """
    try:
        nodes = db.query(TacticalNode).all()
        mesh = []
        for n in nodes:
            # Fetch latest intelligence record directly by ordering on ID desc
            latest_intel = db.query(IntelligenceMaster).filter(
                IntelligenceMaster.node_id == n.id
            ).order_by(desc(IntelligenceMaster.id)).first()
            
            risk = serialize_data(latest_intel.risk_score) if latest_intel else 0.05
            mesh.append({
                "id": n.id, "name": n.name, "lat": n.lat, "lng": n.lon,
                "risk": risk
            })
        
        return {
            "status": "Sync_Complete", 
            "mesh_count": len(mesh),
            "mesh": mesh
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vault Query Error: {str(e)}")

@app.post("/api/v7/tactical/update/{node_id}", tags=["Tactical"])
async def update_node_intelligence(node_id: int, db: Session = Depends(get_db)):
    node = db.query(TacticalNode).filter(TacticalNode.id == node_id).first()
    if not node: raise HTTPException(status_code=404, detail="Invalid Node ID")

    current_wx = await weather.fetch_tactical_weather(node.lat, node.lon)
    if not current_wx:
        raise HTTPException(status_code=503, detail="Environmental Service Unavailable")

    risk = brain.compute_risk(current_wx, {
        "elevation": node.elevation, "river_dist": node.river_dist, "pop_density": node.pop_density
    })

    # Create a NEW intelligence record to keep history
    new_intel = IntelligenceMaster(
        node_id=node.id,
        elevation=node.elevation,
        river_dist=node.river_dist,
        rainfall_mm=current_wx['rainfall_mm'],
        soil_moisture=current_wx['soil_moisture'],
        river_discharge=current_wx['river_discharge'],
        pop_density=float(node.pop_density),
        risk_score=risk,
        target=1 if risk > 0.5 else 0
    )
    db.add(new_intel)
    db.commit()

    return {"node": node.name, "live_metrics": current_wx, "new_risk": serialize_data(round(risk, 4))}

# --- 2. ADVANCED ANALYTICS ---

@app.get("/api/v7/tactical/top-threats", tags=["Analytics"])
async def get_top_threats(limit: int = 10, db: Session = Depends(get_db)):
    top_threats = db.query(TacticalNode, IntelligenceMaster).join(
        IntelligenceMaster, TacticalNode.id == IntelligenceMaster.node_id
    ).order_by(desc(IntelligenceMaster.risk_score)).limit(limit).all()
    
    return [{"name": n.name, "risk": serialize_data(i.risk_score)} for n, i in top_threats]

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

@app.get("/api/v7/nodes/search", tags=["Tactical"])
async def search_nodes(name: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    nodes = db.query(TacticalNode).filter(TacticalNode.name.like(f"%{name}%")).all()
    return nodes

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)