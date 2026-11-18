import numpy as np
import rasterio
from rasterio.transform import from_origin

def create_mock_hyperspectral_tif(filename="sample_farm_200bands.tif"):
    bands = 200
    height = 100
    width = 100

    # Random spectral reflectance values (0.0 to 1.0)
    np.random.seed(42)
    hyperspectral_cube = np.random.uniform(0.05, 0.85, (bands, height, width)).astype(np.float32)

    # Simulate chemical stress (chlorophyll drop) in a specific 20x20 patch
    hyperspectral_cube[40:90, 30:50, 30:50] *= 0.45

    # GPS coordinates matching Sector A farm boundary
    transform = from_origin(78.9500, 20.6050, 0.00025, 0.00025)

    with rasterio.open(
        filename,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=bands,
        dtype="float32",
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(hyperspectral_cube)

    print(f"✅ Created '{filename}' with shape: ({bands} bands, {height}x{width} pixels)")

if __name__ == "__main__":
    create_mock_hyperspectral_tif()