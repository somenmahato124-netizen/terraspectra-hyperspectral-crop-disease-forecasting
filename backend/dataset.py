import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, random_split
from preprocess import process_hyperspectral_image
from spectral_indices import compute_vegetation_indices


class HyperspectralPatchDataset(Dataset):
    """
    Extracts 3D spatial-spectral cubes (1, Bands, Patch_H, Patch_W)
    around each pixel for 3D-CNN crop stress classification.
    """

    def __init__(self, pca_cube: np.ndarray, label_mask: np.ndarray, patch_size: int = 11):
        assert patch_size % 2 == 1, "patch_size must be an odd integer"
        self.patch_size = patch_size
        self.pad = patch_size // 2

        # pca_cube shape: (H, W, C) -> transpose to (C, H, W)
        cube_chw = np.transpose(pca_cube, (2, 0, 1)).astype(np.float32)

        # Reflect-pad spatial dimensions so border pixels also get full patches
        self.padded_cube = np.pad(
            cube_chw,
            pad_width=((0, 0), (self.pad, self.pad), (self.pad, self.pad)),
            mode="reflect"
        )
        self.labels = label_mask.astype(np.int64)
        self.height, self.width = self.labels.shape

    def __len__(self) -> int:
        return self.height * self.width

    def __getitem__(self, idx: int):
        row = idx // self.width
        col = idx % self.width

        patch = self.padded_cube[
            :,
            row : row + self.patch_size,
            col : col + self.patch_size
        ]
        # Add channel dimension for PyTorch Conv3d: (1, Bands, H, W)
        tensor_patch = torch.from_numpy(patch).unsqueeze(0)
        label = torch.tensor(self.labels[row, col], dtype=torch.long)
        return tensor_patch, label


def build_dataloaders(tif_path: str, n_components: int = 15, patch_size: int = 11, batch_size: int = 64):
    reduced_cube, _ = process_hyperspectral_image(tif_path, n_components=n_components)
    indices_info = compute_vegetation_indices(tif_path)
    stress_mask = indices_info["stress_mask"]

    full_dataset = HyperspectralPatchDataset(reduced_cube, stress_mask, patch_size=patch_size)

    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    generator = torch.Generator().manual_seed(42)
    train_ds, val_ds = random_split(full_dataset, [train_size, val_size], generator=generator)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
    return train_loader, val_loader


if __name__ == "__main__":
    train_loader, val_loader = build_dataloaders("sample_farm_200bands.tif")
    sample_x, sample_y = next(iter(train_loader))
    print("📦 PyTorch 3D-CNN Dataset Ready:")
    print(f"   • Train Batches : {len(train_loader)} | Val Batches: {len(val_loader)}")
    print(f"   • Batch X Shape : {tuple(sample_x.shape)}  (Batch, Channel, Spectral, H, W)")
    print(f"   • Batch Y Shape : {tuple(sample_y.shape)}  (0=Healthy, 1=Early Stress)")