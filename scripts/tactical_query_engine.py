from sqlalchemy import create_engine, text
import os
import json

class SentinelSearchEngine:
    def __init__(self):
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        db_file = os.path.join(ROOT_DIR, "tactical_db", "sentinel_v7_tactical.db")
        self.engine = create_engine(f"sqlite:///{db_file}")

    def get_high_risk_zones(self, risk_threshold=0.85):
        """Fetches all nodes that the Bi-LSTM flagged as Extreme Risk."""
        query = text("""
            SELECT n.name, n.lat, n.lon, i.risk_score, n.pop_density
            FROM tactical_nodes n
            JOIN intelligence_master i ON n.id = i.node_id
            WHERE i.risk_score >= :threshold
            LIMIT 100
        """)
        
        with self.engine.connect() as conn:
            result = conn.execute(query, {"threshold": risk_threshold})
            return [dict(row._mapping) for row in result]

    def get_displacement_stats(self):
        """Calculates total projected impact across the Lucknow Division."""
        query = text("""
            SELECT SUM(pop_density * risk_score * 0.45) as total_displacement
            FROM tactical_nodes n
            JOIN intelligence_master i ON n.id = i.node_id
        """)
        with self.engine.connect() as conn:
            return conn.execute(query).scalar()

if __name__ == "__main__":
    # Quick Test
    engine = SentinelSearchEngine()
    print(f"📊 Projected Displacement: {engine.get_displacement_stats():,.0f} people.")