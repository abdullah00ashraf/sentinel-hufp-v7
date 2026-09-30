import httpx
import logging
import asyncio

class WeatherEngine:
    """Deployment-Grade Weather & Hydrology Engine for Lucknow Division."""
    
    # Open-Meteo segregates Weather and Flood data into different API clusters
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
    FLOOD_URL = "https://flood-api.open-meteo.com/v1/flood"

    async def fetch_tactical_weather(self, lat: float, lon: float):
        """Fetches data from Forecast and Flood APIs concurrently to prevent 400 errors."""
        
        # 1. Forecast Parameters (Atmospheric & Soil)
        forecast_params = {
            "latitude": lat, "longitude": lon,
            "current": ["temperature_2m", "precipitation", "surface_pressure", "wind_speed_10m"],
            "hourly": ["soil_moisture_0_to_7cm"],
            "timezone": "auto", "forecast_days": 1
        }

        # 2. Flood Parameters (Legit River Discharge)
        flood_params = {
            "latitude": lat, "longitude": lon,
            "daily": ["river_discharge_max"],
            "forecast_days": 1
        }

        # Using verify=False to bypass local SSL handshake issues if present
        async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
            try:
                # Dispatch both requests in parallel for maximum performance
                f_task = client.get(self.FORECAST_URL, params=forecast_params)
                fl_task = client.get(self.FLOOD_URL, params=flood_params)
                
                responses = await asyncio.gather(f_task, fl_task)
                
                # Verify both responses are 200 OK
                for resp in responses:
                    resp.raise_for_status()

                f_data = responses[0].json()
                fl_data = responses[1].json()

                # Construct the Tactical Intelligence Packet for the Bi-LSTM
                return {
                    "temp_c": f_data['current']['temperature_2m'],
                    "rainfall_mm": f_data['current']['precipitation'],
                    "soil_moisture": f_data['hourly']['soil_moisture_0_to_7cm'][0],
                    "river_discharge": fl_data['daily']['river_discharge_max'][0], # Real Hydrology Data
                    "pressure_hpa": f_data['current']['surface_pressure'],
                    "wind_kmh": f_data['current']['wind_speed_10m']
                }

            except Exception as e:
                logging.error(f"🛰️ Deployment Handshake Failed: {e}")
                return None