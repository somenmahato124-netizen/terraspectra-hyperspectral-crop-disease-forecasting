import torch
import torch.nn as nn


class SpectralSpatialPatchEmbedding(nn.Module):
    """
    Projects a 3D hyperspectral cube (Batch, 1, Bands, H, W) into a sequence
    of spectral-spatial token embeddings with learnable positional encodings.
    """

    def __init__(self, in_bands: int = 15, patch_size: int = 11, embed_dim: int = 64):
        super().__init__()
        self.num_tokens = patch_size * patch_size
        self.proj = nn.Sequential(
            nn.Conv3d(1, embed_dim, kernel_size=(in_bands, 1, 1)),
            nn.BatchNorm3d(embed_dim),
            nn.GELU()
        )
        self.pos_embed = nn.Parameter(torch.randn(1, self.num_tokens, embed_dim) * 0.02)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, 1, Bands, H, W) -> (B, embed_dim, 1, H, W)
        x = self.proj(x).squeeze(2)
        b, c, h, w = x.shape
        # Flatten spatial grid to token sequence: (B, H*W, embed_dim)
        tokens = x.flatten(2).transpose(1, 2)
        return tokens + self.pos_embed


class SpectralViTEncoder(nn.Module):
    """
    Vision Transformer (ViT) encoder block capturing long-range canopy
    context and cross-wavelength spectral relationships via Multi-Head Self-Attention.
    """

    def __init__(
        self,
        in_bands: int = 15,
        patch_size: int = 11,
        embed_dim: int = 64,
        num_heads: int = 4,
        num_layers: int = 2,
        dropout: float = 0.1
    ):
        super().__init__()
        self.embedding = SpectralSpatialPatchEmbedding(in_bands, patch_size, embed_dim)
        self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=embed_dim * 2,
            dropout=dropout,
            activation="gelu",
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.norm = nn.LayerNorm(embed_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        tokens = self.embedding(x)
        batch_size = tokens.size(0)
        cls_tokens = self.cls_token.expand(batch_size, -1, -1)
        seq = torch.cat((cls_tokens, tokens), dim=1)

        encoded = self.transformer(seq)
        cls_output = self.norm(encoded[:, 0])
        return cls_output


if __name__ == "__main__":
    vit_encoder = SpectralViTEncoder(in_bands=15, patch_size=11, embed_dim=64, num_heads=4, num_layers=2)
    sample_cube = torch.randn(8, 1, 15, 11, 11)
    global_features = vit_encoder(sample_cube)
    total_params = sum(p.numel() for p in vit_encoder.parameters() if p.requires_grad)

    print("🔭 Spectral-Spatial Vision Transformer (ViT) Ready:")
    print(f"   • Input Cube Shape      : {tuple(sample_cube.shape)}")
    print(f"   • Global CLS Embedding  : {tuple(global_features.shape)}")
    print(f"   • Trainable Parameters  : {total_params:,}")