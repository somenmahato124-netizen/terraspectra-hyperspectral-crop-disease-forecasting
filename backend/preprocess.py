import rasterio
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def process_hyperspectral_image(file_path, n_components=15):
    print(f"Loading hyperspectral GeoTIFF from: {file_path}")
    
    # 1. Rasterio diye GeoTIFF file open kora
    with rasterio.open(file_path) as src:
        # Read all bands (shape: [bands, height, width])
        image_data = src.read()
        profile = src.profile
        
    print(f"Original Image Shape (Bands, Height, Width): {image_data.shape}")
    
    num_bands, height, width = image_data.shape
    
    # 2. Reshape data for PCA (Expected: [samples, features/bands])
    flattened_data = image_data.reshape(num_bands, height * width).T
    
    # Handle any NaN or infinite values if present
    flattened_data = np.nan_to_num(flattened_data)
    
    # 3. Normalize spectral reflectance values before PCA
    scaler = StandardScaler()
    normalized_data = scaler.fit_transform(flattened_data)
    
    # 4. Apply PCA for Dimensionality Reduction
    print(f"Applying PCA to reduce bands from {num_bands} to {n_components}...")
    pca = PCA(n_components=n_components)
    pca_result = pca.fit_transform(normalized_data)
    
    # 5. Reshape back to image format ([height, width, n_components])
    reduced_image = pca_result.reshape(height, width, n_components)
    variance = np.sum(pca.explained_variance_ratio_) * 100
    
    print(f"PCA Processing Complete! Reduced Shape: {reduced_image.shape}")
    print(f"Total Variance Retained: {variance:.2f}%")
    return reduced_image, profile

# Test run
if __name__ == "__main__":
    sample_path = "sample_farm_200bands.tif"
    processed_img, img_profile = process_hyperspectral_image(sample_path, n_components=15)