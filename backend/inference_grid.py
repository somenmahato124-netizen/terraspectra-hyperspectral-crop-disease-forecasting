import os
import json
import numpy as np
import rasterio
import torch
from preprocess import process_hyperspectral_image
from model_3dcnn import Hybrid3DCNN


def generate_disease_risk_geojson(
    tif_path: str = "sample_farm_200bands.tif",
    checkpoint_path: str = "checkpoints/hybrid_3dcnn_best.pth",
    patch_size: int = 11,
    stride: int = 5
) -> dict:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 1. Load PCA reduced cube & raster transform
    reduced_cube, _ = process_hyperspectral_image(tif_path, n_components=15)
    with rasterio.open(tif_path) as src:
        transform = src.transform

    height, width, bands = reduced_cube.shape
    pad = patch_size // 2
    cube_chw = np.transpose(reduced_cube, (2, 0, 1)).astype(np.float32)
    padded_cube = np.pad(cube_chw, ((0, 0), (pad, pad), (pad, pad)), mode="reflect")

    # 2. Load trained Hybrid 3D-CNN model
    model = Hybrid3DCNN(in_bands=bands, patch_size=patch_size, num_classes=2).to(device)
    if os.path.exists(checkpoint_path):
        model.load_state_dict(torch.load(checkpoint_path, map_location=device))
    model.eval()

    features = []
    with torch.no_grad():
        for r in range(0, height, stride):
            for c in range(0, width, stride):
                patch = padded_cube[:, r : r + patch_size, c : c + patch_size]
                tensor_x = torch.from_numpy(patch).unsqueeze(0).unsqueeze(0).to(device)
                probs = torch.softmax(model(tensor_x), dim=1)
                stress_prob = round(float(probs[0, 1].item()), 4)

                # Convert pixel bounds to geographic coordinates (lon, lat)
                lon_min, lat_max = transform * (c, r)
                lon_max, lat_min = transform * (min(c + stride, width), min(r + stride, height))

                risk_level = (
                    "High Risk" if stress_prob >= 0.65
                    else "Moderate Stress" if stress_prob >= 0.35
                    else "Healthy"
                )

                features.append({
                    "type": "Feature",
                    "properties": {
                        "grid_id": f"cell_{r}_{c}",
                        "stress_probability": stress_prob,
                        "risk_level": risk_level
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [lon_min, lat_min],
                            [lon_max, lat_min],
                            [lon_max, lat_max],
                            [lon_min, lat_max],
                            [lon_min, lat_min]
                        ]]
                    }
                })

    geojson_data = {"type": "FeatureCollection", "features": features}
    os.makedirs("checkpoints", exist_ok=True)
    with open("checkpoints/disease_risk_grid.geojson", "w") as f:
        json.dump(geojson_data, f, indent=2)

    print(f"🗺️ Generated {len(features)} georeferenced risk cells -> checkpoints/disease_risk_grid.geojson")
    return geojson_data


if __name__ == "__main__":
    generate_disease_risk_geojson()