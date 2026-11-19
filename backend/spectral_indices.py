import numpy as np
import rasterio


def compute_vegetation_indices(file_path: str) -> dict:
    """
    Computes NDVI and Red-Edge Chlorophyll Stress Index (NDRE)
    from a 200-band hyperspectral GeoTIFF data cube.
    """
    with rasterio.open(file_path) as src:
        cube = src.read().astype(np.float32)  # Shape: (Bands, Height, Width)

    num_bands, height, width = cube.shape
    if num_bands < 100:
        raise ValueError(f"Expected >= 100 hyperspectral bands, got {num_bands}")

    # Representative band slices across visible red, red-edge, and NIR regions
    red_band = np.mean(cube[25:35, :, :], axis=0)        # ~650-680 nm (Chlorophyll absorption)
    red_edge_band = np.mean(cube[45:55, :, :], axis=0)   # ~705-730 nm (Early stress sensitive)
    nir_band = np.mean(cube[75:90, :, :], axis=0)        # ~800-860 nm (Cell structure reflectance)

    eps = 1e-6

    # 1. Normalized Difference Vegetation Index (NDVI)
    ndvi = (nir_band - red_band) / (nir_band + red_band + eps)
    ndvi = np.clip(ndvi, -1.0, 1.0)

    # 2. Normalized Difference Red-Edge Index (NDRE) for early pre-symptomatic stress
    ndre = (nir_band - red_edge_band) / (nir_band + red_edge_band + eps)
    ndre = np.clip(ndre, -1.0, 1.0)

    # 3. Classify pixel health status based on NDRE threshold
    stressed_mask = ndre < 0.15
    total_pixels = height * width
    stressed_pixels = int(np.sum(stressed_mask))
    healthy_pixels = total_pixels - stressed_pixels
    stress_percentage = round((stressed_pixels / total_pixels) * 100, 2)

    return {
        "grid_shape": [height, width],
        "mean_ndvi": round(float(np.mean(ndvi)), 4),
        "mean_ndre": round(float(np.mean(ndre)), 4),
        "healthy_pixels": healthy_pixels,
        "stressed_pixels": stressed_pixels,
        "early_stress_percent": stress_percentage,
        "stress_mask": stressed_mask.astype(np.uint8)
    }


if __name__ == "__main__":
    sample_tif = "sample_farm_200bands.tif"
    results = compute_vegetation_indices(sample_tif)
    print("🌿 Hyperspectral Vegetation Indices Summary:")
    print(f"   • Grid Size         : {results['grid_shape'][0]}x{results['grid_shape'][1]} px")
    print(f"   • Mean NDVI         : {results['mean_ndvi']}")
    print(f"   • Mean NDRE         : {results['mean_ndre']}")
    print(f"   • Healthy Pixels    : {results['healthy_pixels']}")
    print(f"   • Early Stress Area : {results['stressed_pixels']} px ({results['early_stress_percent']}%)")