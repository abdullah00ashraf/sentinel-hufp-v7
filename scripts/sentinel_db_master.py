import os
import json
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# --- AUTOMATED DIRECTORY HANDSHAKE ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FOLDER = os.path.join(ROOT_DIR, "tactical_db")

# Create the folder if it doesn't exist
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

# Path to the actual database file inside the new folder
DB_PATH = f"sqlite:///{os.path.join(DB_FOLDER, 'sentinel_v7_tactical.db')}"
Base = declarative_base()

# --- SCHEMA DEFINITION (The Intelligence Octet) ---

class TacticalNode(Base):
    __tablename__ = 'tactical_nodes'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    elevation = Column(Float)
    pop_density = Column(Integer)
    river_dist = Column(Float)

class HydrologyRegistry(Base):
    __tablename__ = 'hydrology_registry'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    river_discharge = Column(Float)
    rainfall_mm = Column(Float)
    soil_moisture = Column(Float)

class IntelligenceMaster(Base):
    """The 'Heavy' Table for 80M-Row Compatibility."""
    __tablename__ = 'intelligence_master'
    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey('tactical_nodes.id'))
    hydro_id = Column(Integer, ForeignKey('hydrology_registry.id'))
    runoff_mm = Column(Float)
    sar_vh = Column(Float)
    risk_score = Column(Float) 
    target_class = Column(Integer) 

class MissionAudit(Base):
    __tablename__ = 'mission_audits'
    id = Column(Integer, primary_key=True)
    event_type = Column(String) 
    details = Column(Text)
    metrics_json = Column(Text) 

# --- INITIALIZATION & MIGRATION ENGINE ---

def initialize_tactical_db():
    print("🛡️  Sentinel V7.0: Constructing Tactical Database...")
    
    # FIX: Changed create_all to create_engine
    engine = create_engine(DB_PATH)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()

    # Phase 1: Migrate Localities (The Mesh)
    mesh_path = os.path.join(ROOT_DIR, "data", "geospatial", "localities.json")
    if os.path.exists(mesh_path):
        with open(mesh_path, 'r') as f:
            mesh_data = json.load(f)
            for node in mesh_data:
                db_node = TacticalNode(
                    name=node['name'], lat=node['lat'], lon=node['lon'],
                    elevation=node['elevation'], pop_density=node.get('pop_density', 1500),
                    river_dist=node['river_dist']
                )
                session.add(db_node)
        session.commit()
        print(f"   ✅ Migrated {len(mesh_data)} Tactical Nodes to DB.")

    # Phase 2: Migrate Training Logs (Mission Audits)
    report_path = os.path.join(ROOT_DIR, "TACTICAL_VALIDATION_REPORT.json")
    if os.path.exists(report_path):
        with open(report_path, 'r') as f:
            report = json.load(f)
            audit = MissionAudit(
                event_type='MASTER_VALIDATION',
                details='Post-Training 10M Monte Carlo Stress Test',
                metrics_json=json.dumps(report)
            )
            session.add(audit)
        session.commit()
        print("   ✅ Migrated Validation Report to Audit Registry.")

    print(f"\n🚀 DATABASE DEPLOYED AT: {DB_PATH}")

if __name__ == "__main__":
    initialize_tactical_db()