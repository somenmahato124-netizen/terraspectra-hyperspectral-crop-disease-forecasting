import rasterio
import numpy as np
from sklearn.decomposition import PCA

def process_hyperspectral_image(file_path):
    print(f"Loading hyperspectral GeoTIFF from: {file_path}")
    
    # 1. Rasterio diye GeoTIFF file open kora
    with rasterio.open(file_path) as src:
        # Read all bands (shape: [bands, height, width])
        image_data = src.read()
        profile = src.profile
        
    print(f"Original Image Shape (Bands, Height, Width): {image_data.shape}")
    
    num_bands, height, width = image_data.shape
    
    # 2. Reshape data for PCA (Expected: [samples, features/bands])
    # Samples = height * width, Features = num_bands
    flattened_data = image_data.reshape(num_bands, height * width).T
    
    # Handle any NaN or infinite values if present
    flattened_data = np.nan_to_num(flattened_data)
    
    # 3. Apply PCA for Dimensionality Reduction (e.g., reducing to 3 principal components)
    n_components = 3
    print(f"Applying PCA to reduce bands from {num_bands} to {n_components}...")
    pca = PCA(n_components=n_components)
    pca_result = pca.fit_transform(flattened_data)
    
    # 4. Reshape back to image format ([height, width, n_components])
    reduced_image = pca_result.reshape(height, width, n_components)
    
    print("PCA Processing Complete!")
    return reduced_image, profile

# Test run (Jokhon apnar kase kono sample GeoTIFF file thakbe)
if __name__ == "__main__":
    # sample_path = "path_to_your_raster.tif"
    # processed_img, img_profile = process_hyperspectral_image(sample_path)
    print("Preprocess script is ready!")