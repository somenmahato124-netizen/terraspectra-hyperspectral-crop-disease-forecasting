import torch
import torch.nn as nn


class Hybrid3DCNN(nn.Module):
    """
    Hybrid 3D-2D Convolutional Neural Network for Hyperspectral Crop Stress Detection.
    Extracts joint spectral-spatial features via 3D convolutions followed by 2D spatial refinement.
    Input shape: (Batch, 1, Spectral_Bands=15, Height=11, Width=11)
    """

    def __init__(self, in_bands: int = 15, patch_size: int = 11, num_classes: int = 2):
        super().__init__()

        # Block 1: Joint Spectral-Spatial 3D Feature Extraction
        self.conv3d_block1 = nn.Sequential(
            nn.Conv3d(in_channels=1, out_channels=8, kernel_size=(5, 3, 3), padding=(0, 1, 1)),
            nn.BatchNorm3d(8),
            nn.ReLU(inplace=True)
        )

        # Block 2: Deeper Spectral-Spatial Compression
        self.conv3d_block2 = nn.Sequential(
            nn.Conv3d(in_channels=8, out_channels=16, kernel_size=(3, 3, 3), padding=(0, 1, 1)),
            nn.BatchNorm3d(16),
            nn.ReLU(inplace=True)
        )

        # Remaining spectral depth after 3D convs: in_bands - 4 - 2 = in_bands - 6
        reduced_bands = in_bands - 6
        flattened_channels = 16 * reduced_bands

        # Block 3: 2D Spatial Feature Refinement
        self.conv2d_block = nn.Sequential(
            nn.Conv2d(in_channels=flattened_channels, out_channels=64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((3, 3))
        )

        # Classification Head
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 3 * 3, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.3),
            nn.Linear(128, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv3d_block1(x)
        x = self.conv3d_block2(x)

        # Collapse channel & spectral dimensions for 2D spatial convolution
        batch_size, channels, spectral, height, width = x.shape
        x = x.view(batch_size, channels * spectral, height, width)

        x = self.conv2d_block(x)
        logits = self.classifier(x)
        return logits


def count_trainable_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


if __name__ == "__main__":
    model = Hybrid3DCNN(in_bands=15, patch_size=11, num_classes=2)
    dummy_input = torch.randn(8, 1, 15, 11, 11)
    output_logits = model(dummy_input)
    probs = torch.softmax(output_logits, dim=1)

    print("🧠 Hybrid 3D-CNN Architecture Initialized:")
    print(f"   • Input Tensor Shape   : {tuple(dummy_input.shape)}")
    print(f"   • Output Logits Shape  : {tuple(output_logits.shape)}")
    print(f"   • Trainable Parameters : {count_trainable_parameters(model):,}")
    print(f"   • Sample Probabilities : {probs[0].detach().numpy().round(4)}")