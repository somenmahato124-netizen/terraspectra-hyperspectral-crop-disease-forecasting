
import numpy as np
import rasterio
from rasterio.transform import from_origin

# 200 spectral bands, 100x100 pixels mock data
data = np.random.rand(200, 100, 100).astype(np.float32)
transform = from_origin(78.9500, 20.6050, 0.00025, 0.00025)

with rasterio.open(
    'mock_farm_hyperspectral.tif', 'w',
    driver='GTiff', height=100, width=100,
    count=200, dtype='float32',
    crs='+proj=latlong', transform=transform
) as dst:
    dst.write(data)

print("Mock 200-band GeoTIFF created!")