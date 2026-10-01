# Sentinel V7: Spatiotemporal Neural Core & PINN Hydrology Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: >=3.10](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Hugging Face PyTorch PINN](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-20M%20PyTorch%20PINN-blue.svg)](https://huggingface.co/abdullahashraf122/sentinel-mumbai-pinn-v1)
[![Hugging Face Model](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Deep%20Flood%20LSTM-orange.svg)](https://huggingface.co/abdullahashraf122/sentinel-v7-deep-flood-lstm)
[![Hugging Face Hybrid PINN](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Hybrid%20PINN%20Keras-red.svg)](https://huggingface.co/abdullahashraf122/sentinel-mumbai-hybrid-pinn-keras)
[![Hugging Face Dataset](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-83.9M%20Vector%20Dataset-yellow.svg)](https://huggingface.co/datasets/abdullahashraf122/lucknow_hufp_datasets)
[![Hugging Face Parquet](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-27.8GB%20Parquet-darkgreen.svg)](https://huggingface.co/datasets/abdullahashraf122/mumbai-salsette-flood-intelligence-2005-2023)
[![Framework: FastAPI](https://img.shields.io/badge/Framework-FastAPI-teal.svg)](https://fastapi.tiangolo.com/)
[![Deep Learning: Keras / PyTorch](https://img.shields.io/badge/DL-Bi--LSTM%20%7C%20PINN-red.svg)](https://keras.io/)
[![Explainable AI: SHAP / LIME](https://img.shields.io/badge/XAI-SHAP%20%26%20LIME-yellow.svg)](#explainable-ai)

**Sentinel V7 (HUFP_SENTINEL_V6)** is the deep-learning analytical engine and spatiotemporal neural core of **Project Salsette**. It provides spatiotemporal neural network inference, out-of-distribution (OOD) stress testing, mathematical loss manifold auditing, and explainability extraction for regional flood forecasting and hydrological risk management.

The core predictive engine is a **Bi-Directional LSTM neural network** constrained by **Physics-Informed Neural Network (PINN)** hydrodynamic boundaries. Trained on spatiotemporal remote sensing and hydrological telemetry datasets combining rainfall, elevation, river discharge, soil moisture, and Synthetic Aperture Radar (SAR) satellite data, the engine achieves an inference latency of **0.668 ms per 100 geospatial nodes** with full **SHAP/LIME Explainable AI (XAI)** feature attribution.

---

## 1. Neural Architecture & Calibration Pipeline

```mermaid
graph TD
    RawData["Hydrological Telemetry & Satellite Ingestion"] --> Preprocess["Feature Scaling & Octet Normalization"]
    Preprocess --> ModelCore["Neural Core: Bi-Directional LSTM (bi_lstm_flood_model.keras)"]

    GeoInputs["8-Dimensional Feature Octet (core/models.py)"] --> Predictor["Tactical Predictor (core/predictor.py)"]
    ModelCore --> Predictor

    subgraph PINN_Boundary_Enforcement["PINN Hydrodynamic Boundary Layer"]
        Predictor --> BaseAI["Raw Neural Probability (0.0 to 1.0)"]
        Predictor --> TopoPenalty["Topographic Penalty (elevation depression)"]
        Predictor --> DischargeRatio["River Discharge Ratio (carrying capacity)"]
        Predictor --> RainRatio["Precipitation Ratio (surface saturation)"]
    end

    BaseAI --> Synthesis["Synthesized Calibrated Flood Risk Score"]
    TopoPenalty --> Synthesis
    DischargeRatio --> Synthesis
    RainRatio --> Synthesis

    Synthesis --> API["FastAPI Tactical Hub (api/main.py)"]
    Synthesis --> Auditor["Loss Manifold & Convergence Audit (convergence_auditor.py)"]
    Synthesis --> XAI["SHAP/LIME Feature Attribution (xai_explainability_auditor.py)"]
```

---

## 2. The 8-Dimensional Feature Octet

Every geospatial node in the network is evaluated over an 8-dimensional feature vector:

| Feature Name | Dimension / Unit | Physical Significance |
|---|---|---|
| `elevation` | Meters ($m$) | Digital Elevation Model (DEM) height; identifies natural retention depressions. |
| `river_dist` | Kilometers ($km$) | Euclidean proximity to major river channels and drainage creeks. |
| `rainfall_mm` | Millimeters ($mm$) | Accumulated surface precipitation over the evaluation timestep. |
| `runoff_mm` | Millimeters ($mm$) | Overland surface runoff derived from soil infiltration curves. |
| `soil_moisture` | Saturation Index $[0.0, 1.0]$ | Pre-existing groundwater saturation coefficient (antecedent moisture condition). |
| `river_discharge` | Flow Rate ($\text{m}^3/\text{s}$) | Active channel volume (calibrated against river bankfull threshold: $1,311.20\text{ m}^3/\text{s}$). |
| `pop_density` | Inhabitants / cell | Demographic exposure weighting extracted from global population models. |
| `sar_vh` | Backscatter ($\text{dB}$) | Sentinel-1 Synthetic Aperture Radar cross-polarization ground water reflection. |

---

## 3. Project Directory Structure

```
HUFP_SENTINEL_V6/
├── api/                   # Tactical FastAPI Application & Brain Proxy
│   ├── brain_proxy.py     # High-throughput asynchronous prediction router
│   ├── main.py            # Primary REST API endpoints
│   └── weather_engine.py  # Live atmospheric & hydrological fetcher
├── audits/                # Validation reports & Monte Carlo paradox registries
├── brain/                 # Neural Network Checkpoints & Weights
│   ├── bi_lstm_flood_model.keras  # Calibrated Production Bi-LSTM
│   └── scaler.joblib      # RobustScaler normalization coefficients
├── core/                  # Core Hydrology, Predictor & Database Models
│   ├── db_manager.py      # SQLite / Master database connection pool
│   ├── models.py          # SQLAlchemy models (TacticalNode, MissionAudit)
│   ├── predictor.py       # PINN boundary layer & calibration logic
│   └── weather_service.py # Open-Meteo environmental cluster client
├── scripts/               # Master validator, stress test, and audit suites
├── web/                   # Command Center UI & Model Info dashboards
│   ├── index.html
│   └── model_info.html
├── convergence_auditor.py # Mathematical loss manifold & gradient convergence test
├── xai_explainability_auditor.py # SHAP waterfall & LIME attribution generator
└── requirements.txt       # Production dependencies
```

---

## 4. Quickstart & Installation

### Prerequisites
- Python 3.10+
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/abdullah00ashraf/sentinel-hufp-v7.git
   cd sentinel-hufp-v7
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration:**
   ```bash
   cp .env.example .env
   ```

### Running the Tactical API Server

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive API documentation will be available at:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Running Convergence & XAI Audits

```bash
# Run gradient loss manifold convergence audit
python convergence_auditor.py

# Run SHAP / LIME explainability extraction
python xai_explainability_auditor.py
```

---

## 5. API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Tactical Hub health and status |
| `GET` | `/api/tactical/nodes` | List active geospatial nodes with coordinates |
| `POST`| `/api/predict` | Compute calibrated flood probability and PINN boundaries |
| `GET` | `/api/weather/live` | Retrieve real-time atmospheric and river discharge telemetry |
| `GET` | `/api/audits/latest` | Retrieve latest Monte Carlo stress audit metrics |

---

## 6. 🤗 Pretrained Models & Datasets on Hugging Face Hub
The neural models, PINN loss manifolds, and multi-gigabyte remote sensing datasets powering Sentinel V7 are published and versioned on Hugging Face:

### 1. Neural Sequence & PINN Models
* **`sentinel-mumbai-pinn-v1`** (PyTorch, 20,387,457 Parameters):  
  [`https://huggingface.co/abdullahashraf122/sentinel-mumbai-pinn-v1`](https://huggingface.co/abdullahashraf122/sentinel-mumbai-pinn-v1)  
  *6-Layer Bi-LSTM with Self-Attention, trained under combined Log-Cosh Data Loss and Hydraulic Lock Mass Conservation loss manifold.*
* **`sentinel-v7-deep-flood-lstm`** (Keras 3 / TensorFlow):  
  [`https://huggingface.co/abdullahashraf122/sentinel-v7-deep-flood-lstm`](https://huggingface.co/abdullahashraf122/sentinel-v7-deep-flood-lstm)  
  *Dual Bi-LSTM neural sequence model with fitted 8-feature `scaler.joblib` and self-contained `inference.py`.*
* **`sentinel-mumbai-hybrid-pinn-keras`** (Keras 3 / Mixed Precision):  
  [`https://huggingface.co/abdullahashraf122/sentinel-mumbai-hybrid-pinn-keras`](https://huggingface.co/abdullahashraf122/sentinel-mumbai-hybrid-pinn-keras)  
  *Attention-augmented PINN enforcing continuity PDE residual $\frac{\partial \hat{y}}{\partial t} - (\text{Rain} - \text{Infil}) = 0$.*

### 2. Spatiotemporal & Remote Sensing Datasets
* **`lucknow_hufp_datasets`** (2.88 GB, 83,986,875 samples):  
  [`https://huggingface.co/datasets/abdullahashraf122/lucknow_hufp_datasets`](https://huggingface.co/datasets/abdullahashraf122/lucknow_hufp_datasets)  
  *Memory-mapped NumPy feature matrices (`features_80m.npy` of shape `[83986875, 8]` and `labels_80m.npy`) fusing Copernicus Sentinel-1 SAR backscatter with HydroSHEDS and GEOGloWS discharge.*
* **`mumbai-salsette-flood-intelligence-2005-2023`** (27.84 GB Parquet, 633,279,552 rows):  
  [`https://huggingface.co/datasets/abdullahashraf122/mumbai-salsette-flood-intelligence-2005-2023`](https://huggingface.co/datasets/abdullahashraf122/mumbai-salsette-flood-intelligence-2005-2023)  
  *19 annual multi-decadal Parquet partitions across 216,284 spatial cells, ERA5 weather, 1-min MCGM tides, and Sentinel-1 SAR.*

```python
# Quickstart A: PyTorch 20M PINN Inference
from huggingface_hub import hf_hub_download
import torch

weights_path = hf_hub_download(repo_id="abdullahashraf122/sentinel-mumbai-pinn-v1", filename="sentinel_mumbai_v1.pt")
state_dict = torch.load(weights_path, map_location="cpu")
print(f"Loaded 20M PINN state dict with {len(state_dict)} tensor keys.")

# Quickstart B: Keras Bi-LSTM with Fitted Scaler
from huggingface_hub import hf_hub_download
import keras
import joblib
import numpy as np

model_path = hf_hub_download(repo_id="abdullahashraf122/sentinel-v7-deep-flood-lstm", filename="bi_lstm_flood_model_v7_deep.keras")
scaler_path = hf_hub_download(repo_id="abdullahashraf122/sentinel-v7-deep-flood-lstm", filename="scaler.joblib")

model = keras.models.load_model(model_path)
scaler = joblib.load(scaler_path)

# Predict on raw 8-dimensional telemetry octet:
# [elevation, river_dist, rainfall_mm, runoff_mm, soil_moisture, river_discharge, pop_density, sar_vh]
raw_sample = np.array([[120.0, 1.2, 145.0, 43.5, 0.88, 1250.0, 3500.0, -28.5]])
scaled = scaler.transform(raw_sample).reshape(1, 1, 8)
risk = float(model.predict(scaled, verbose=0)[0, 0])
print(f"Predicted Flood Vulnerability: {risk:.4f}")
```

---

## 7. License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.
