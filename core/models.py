import os
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Text, Index
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class TacticalNode(Base):
    """Stores the geospatial mesh of Lucknow."""
    __tablename__ = 'tactical_nodes'
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    elevation = Column(Float)
    pop_density = Column(Integer)
    river_dist = Column(Float)
    
    # Relationship for easier querying
    intelligence = relationship("IntelligenceMaster", back_populates="node")

class IntelligenceMaster(Base):
    """
    The High-Velocity Core. 
    Synchronized with CSV headers: elevation, river_dist, rainfall_mm, etc.
    """
    __tablename__ = 'intelligence_master'
    id = Column(Integer, primary_key=True)
    
    # Missing Link Fixed: Connects to TacticalNode
    node_id = Column(Integer, ForeignKey('tactical_nodes.id'), index=True)
    
    # Feature Octet
    elevation = Column(Float)
    river_dist = Column(Float)
    rainfall_mm = Column(Float)
    runoff_mm = Column(Float)
    soil_moisture = Column(Float)
    river_discharge = Column(Float)
    pop_density = Column(Float)
    sar_vh = Column(Float)
    
    # Results
    risk_score = Column(Float, index=True, nullable=True) 
    target = Column(Integer, index=True) 

    # Relationship back to node
    node = relationship("TacticalNode", back_populates="intelligence")

    # Performance Indexing
    __table_args__ = (Index('idx_hydro_search', "river_discharge", "risk_score"),)

class MissionAudit(Base):
    """The 'Black Box' for training and validation logs."""
    __tablename__ = 'mission_audits'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String, index=True)
    details = Column(Text)
    metrics_json = Column(Text)