from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from preprocess import process_hyperspectral_image

app = FastAPI(title="TerraSpectra Geospatial API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SAMPLE_TIF = "sample_farm_200bands.tif"

@app.get("/")
def health_check():
    return {"status": "online", "service": "TerraSpectra Hyperspectral API"}

@app.get("/api/farm-metadata")
def get_farm_metadata():
    if not os.path.exists(SAMPLE_TIF):
        raise HTTPException(status_code=404, detail="Hyperspectral raster not found")

    reduced_cube, profile = process_hyperspectral_image(SAMPLE_TIF, n_components=15)
    height, width, n_components = reduced_cube.shape

    return {
        "sector_name": "Sector A - Wheat & Paddy Farm",
        "total_acres": 1000,
        "original_bands": int(profile.get("count", 200)),
        "pca_components": int(n_components),
        "grid_dimensions": {"height": int(height), "width": int(width)},
        "crs": str(profile.get("crs", "EPSG:4326")),
        "status": "PCA Preprocessed & Ready for 3D-CNN"
    }