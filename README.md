# TerraSpectra: Hyperspectral Crop Disease Forecasting

**Domain:** Precision Agriculture & Advanced Computer Vision

## 📌 Project Overview
Traditional satellite crop monitoring relies on standard RGB or simple infrared imagery, which only detects crop diseases after leaves turn yellow or brown—often too late to save the harvest. **TerraSpectra** ingests hyperspectral satellite imagery (200+ spectral bands invisible to the human eye) and uses a **3D-CNN + Vision Transformer (ViT)** hybrid architecture to detect subtle chemical anomalies in plant chlorophyll reflection up to **three weeks before visible symptoms appear**.

---

## 🛠️ Tech Stack
* **Frontend & GIS:** React, Vite, Mapbox GL JS, Deck.gl
* **Backend & Inference API:** Python, FastAPI, Uvicorn
* **Geospatial & ML Pipeline:** Rasterio, NumPy, Scikit-learn (PCA), PyTorch

---

## 📂 Project Structure
```text
Terra Spectra/
├── backend/
│   ├── main.py          # FastAPI server & REST endpoints
│   └── preprocess.py    # Rasterio GeoTIFF parsing & PCA dimensionality reduction
├── frontend/
│   ├── src/             # React components & Mapbox/Deck.gl GIS integration
│   └── package.json
├── notebooks/           # Jupyter notebooks for spectral exploration & testing
├── .gitignore
└── README.md
```

---

## 🚀 Development Roadmap & Progress

### ✅ Week 1: Data Preparation & Map Scaffolding (Completed)
- [x] **Geospatial Pipeline:** Set up Python environment and built `preprocess.py` using `Rasterio` to parse multi-band hyperspectral GeoTIFF cubes.
- [x] **Dimensionality Reduction:** Implemented Principal Component Analysis (PCA) to reduce 200+ spectral bands into manageable components.
- [x] **Backend Foundation:** Initialized FastAPI server with CORS middleware.
- [x] **GIS Interface:** Built React + Vite frontend integrated with Mapbox GL JS and Deck.gl to render base geographical farm layers.

### 🔜 Upcoming Milestones
- **Week 2:** Build Hybrid 3D-CNN model in PyTorch & render colored disease risk pixel grids on the 3D map.
- **Week 3:** Integrate Vision Transformer (ViT) self-attention mechanism & build frontend analytics sidebar charts.
- **Week 4:** Wrap inference model in FastAPI with raster tiling algorithm & add historical timeline sliders.

---

## ⚙️ Local Setup & Installation

### 1. Backend Setup
```bash
cd backend
pip install fastapi uvicorn rasterio numpy scikit-learn
uvicorn main:app --reload
```
The API will run at `http://127.0.0.1:8000`.

### 2. Frontend Setup
```bash
cd frontend
npm install
```
Create a `.env` file inside `frontend/` and add your Mapbox public token:
```env
VITE_MAPBOX_TOKEN=your_mapbox_access_token_here
```
Start the development server:
```bash
npm run dev
```
The application will run at `http://localhost:5173`.