import os
import json
import torch
import torch.nn as nn
from torch.optim import Adam
from dataset import build_dataloaders
from model_3dcnn import Hybrid3DCNN


def evaluate(model: nn.Module, val_loader, criterion, device: torch.device) -> dict:
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    tp = fp = fn = 0

    with torch.no_grad():
        for patches, labels in val_loader:
            patches, labels = patches.to(device), labels.to(device)
            outputs = model(patches)
            loss = criterion(outputs, labels)

            total_loss += loss.item() * patches.size(0)
            preds = torch.argmax(outputs, dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

            tp += ((preds == 1) & (labels == 1)).sum().item()
            fp += ((preds == 1) & (labels == 0)).sum().item()
            fn += ((preds == 0) & (labels == 1)).sum().item()

    precision = tp / (tp + fp + 1e-8)
    recall = tp / (tp + fn + 1e-8)
    f1_score = 2 * precision * recall / (precision + recall + 1e-8)

    return {
        "val_loss": round(total_loss / max(total, 1), 4),
        "val_accuracy": round((correct / max(total, 1)) * 100, 2),
        "f1_score": round(f1_score, 4)
    }


def train_model(tif_path: str = "sample_farm_200bands.tif", epochs: int = 5, lr: float = 1e-3):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🚀 Training Hybrid 3D-CNN on device: {device}")

    train_loader, val_loader = build_dataloaders(tif_path, n_components=15, patch_size=11, batch_size=64)
    model = Hybrid3DCNN(in_bands=15, patch_size=11, num_classes=2).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = Adam(model.parameters(), lr=lr, weight_decay=1e-4)

    os.makedirs("checkpoints", exist_ok=True)
    best_acc = 0.0
    history = []

    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        train_correct = 0
        train_total = 0

        for patches, labels in train_loader:
            patches, labels = patches.to(device), labels.to(device)
            optimizer.zero_grad()

            outputs = model(patches)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * patches.size(0)
            preds = torch.argmax(outputs, dim=1)
            train_correct += (preds == labels).sum().item()
            train_total += labels.size(0)

        train_loss = round(running_loss / max(train_total, 1), 4)
        train_acc = round((train_correct / max(train_total, 1)) * 100, 2)
        val_metrics = evaluate(model, val_loader, criterion, device)

        epoch_log = {"epoch": epoch, "train_loss": train_loss, "train_acc": train_acc, **val_metrics}
        history.append(epoch_log)

        print(
            f"Epoch [{epoch}/{epochs}] | Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}% | "
            f"Val Acc: {val_metrics['val_accuracy']:.2f}% | F1: {val_metrics['f1_score']:.4f}"
        )

        if val_metrics["val_accuracy"] >= best_acc:
            best_acc = val_metrics["val_accuracy"]
            torch.save(model.state_dict(), "checkpoints/hybrid_3dcnn_best.pth")

    with open("checkpoints/training_metrics.json", "w") as f:
        json.dump(history, f, indent=2)

    print(f"✅ Training Complete! Best Validation Accuracy: {best_acc:.2f}%")


if __name__ == "__main__":
    train_model(epochs=5)