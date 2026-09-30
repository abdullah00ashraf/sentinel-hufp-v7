import os, json
import numpy as np
import pandas as pd
import rasterio
from .predictor import SentinelPredictor

class SentinelEngineV7:
    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.POP_DATA = os.path.join(self.BASE_DIR, "data", "geospatial", "lucknow_population.tif")
        self.HYDRO_DATA = os.path.join(self.BASE_DIR, "data", "hydrology", "lucknow_flood_hist_19_21.csv")
        self.GRID_PATH = os.path.join(self.BASE_DIR, "data", "geospatial", "localities.json")
        
        self.predictor = SentinelPredictor()

        # 15 STRATEGIC HUBS (Demographic & Infrastructure Anchors)
        self.MAJOR_HUBS = [
            {"name": "Hazratganj", "lat": 26.850, "lon": 80.940, "elev": 72.0, "dist": 0.8, "pop": 45000},
            {"name": "Gomti Nagar", "lat": 26.865, "lon": 80.995, "elev": 68.0, "dist": 0.3, "pop": 85000},
            {"name": "Aliganj", "lat": 26.895, "lon": 80.935, "elev": 78.0, "dist": 2.1, "pop": 60000},
            {"name": "Indira Nagar", "lat": 26.885, "lon": 81.005, "elev": 75.0, "dist": 1.8, "pop": 120000},
            {"name": "Chowk", "lat": 26.872, "lon": 80.915, "elev": 64.0, "dist": 0.4, "pop": 95000},
            {"name": "Charbagh", "lat": 26.832, "lon": 80.922, "elev": 71.0, "dist": 2.5, "pop": 35000},
            {"name": "Aminabad", "lat": 26.845, "lon": 80.932, "elev": 65.0, "dist": 1.2, "pop": 55000},
            {"name": "Jankipuram", "lat": 26.915, "lon": 80.955, "elev": 77.0, "dist": 1.5, "pop": 70000},
            {"name": "Vikas Nagar", "lat": 26.892, "lon": 80.955, "elev": 76.0, "dist": 1.1, "pop": 40000},
            {"name": "Mahanagar", "lat": 26.875, "lon": 80.950, "elev": 74.0, "dist": 0.6, "pop": 30000},
            {"name": "Rajajipuram", "lat": 26.842, "lon": 80.895, "elev": 69.0, "dist": 3.2, "pop": 50000},
            {"name": "Amausi Airport", "lat": 26.762, "lon": 80.885, "elev": 60.0, "dist": 4.5, "pop": 12000},
            {"name": "Sarojini Nagar", "lat": 26.785, "lon": 80.865, "elev": 58.0, "dist": 5.1, "pop": 25000},
            {"name": "Chinhat", "lat": 26.892, "lon": 81.045, "elev": 70.0, "dist": 0.9, "pop": 40000},
            {"name": "Ashiyana", "lat": 26.802, "lon": 80.915, "elev": 63.0, "dist": 2.8, "pop": 65000}
        ]

        print("🛡️ Sentinel V7.0: Initializing Production Multimodal Engine...")
        if os.path.exists(self.GRID_PATH):
            with open(self.GRID_PATH, 'r') as f:
                self.zones_mesh = json.load(f)
        else:
            self.zones_mesh = []
        
        # Load Hydrology for Discharge Constraints
        if os.path.exists(self.HYDRO_DATA):
            self.hydro_df = pd.read_csv(self.HYDRO_DATA)
            self.max_discharge = float(self.hydro_df['river_discharge'].max()) # 1311.20 m3/s
            self.mean_discharge = float(self.hydro_df['river_discharge'].mean())
        else:
            self.max_discharge = 1311.20
            self.mean_discharge = 300.0

    def get_pop_density(self, lat, lon):
        try:
            with rasterio.open(self.POP_DATA) as src:
                row, col = src.index(lon, lat)
                return max(0, int(src.read(1)[row, col]))
        except: return 500 # Fallback density per 100m

    def predict_city_state(self, manual_rain=None):
        rain = float(manual_rain) if manual_rain else 0.0
        runoff, soil = rain * 0.22, min(0.95, 0.45 + (rain * 0.005))
        discharge = self.mean_discharge + (rain * 2.5)

        combined = []
        for z in self.zones_mesh:
            combined.append({
                **z, "is_hub": False,
                "elevation": z.get('elevation', 70.0),
                "river_dist": z.get('river_dist', 2.0),
                "pop": self.get_pop_density(z['lat'], z['lon'])
            })
        for h in self.MAJOR_HUBS:
            combined.append({
                **h, "is_hub": True,
                "elevation": h['elev'],
                "river_dist": h['dist']
            })

        # Assemble feature packet for SentinelPredictor
        feature_dicts = []
        for p in combined:
            feature_dicts.append({
                'elevation': float(p['elevation']),
                'river_dist': float(p['river_dist']),
                'rainfall_mm': rain,
                'runoff_mm': runoff,
                'soil_moisture': soil,
                'river_discharge': discharge,
                'pop_density': float(p.get('pop', 1500)),
                'sar_vh': 49.0
            })

        # Unified Calibrated Risk Inference
        risk_scores = self.predictor.predict_risk(feature_dicts)

        refined = []
        for i, p in enumerate(combined):
            risk = float(risk_scores[i])
            displaced = int((p['pop'] * (risk / 100.0)) * 0.42) if risk > 35.0 else 0
            
            refined.append({
                "name": p.get('name', 'Tactical Node'),
                "lat": p['lat'],
                "lon": p.get('lon', p.get('lng', 80.940)),
                "risk": risk,
                "elevation": p['elevation'],
                "is_hub": p['is_hub'],
                "impact": {
                    "displaced": displaced,
                    "duration": f"{round((risk / 15.0) + (rain / 35.0), 1)} days",
                    "casualties": int(displaced * 0.003) if risk > 85.0 else 0,
                    "area_affected": f"{round(risk * 0.18, 2)} sq km"
                }
            })
        return refined

sentinel = SentinelEngineV7()