import argparse
import os
import random
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from torch.amp import autocast, GradScaler

from src.data.dataset import MultispectralWaterDataset
from src.models.unet import MultispectralUNet
from src.losses.combined_loss import CombinedWaterLoss
from src.metrics.evaluator import SegmentationMetrics


def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def parse_args():
    parser = argparse.ArgumentParser(description="Train Multispectral U-Net for Satellite Water Segmentation")
    parser.add_argument("--data_dir", type=str, default="data", help="Root data directory containing images/ and labels/")
    parser.add_argument("--metadata_csv", type=str, default="metadata.csv", help="Path to metadata.csv")
    parser.add_argument("--in_channels", type=int, default=6, choices=[6, 12], help="Number of input spectral bands")
    parser.add_argument("--synthetic_dir", type=str, default=None, help="Optional directory containing synthetic scenes")
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs (default: 100)")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--output_model", type=str, default="unet_best.pth", help="Path to save best model checkpoint")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    return parser.parse_args()


def main():
    args = parse_args()
    set_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Executing on device: {device} | Spectral Channels: {args.in_channels}")

    images_dir = os.path.join(args.data_dir, "images")
    labels_dir = os.path.join(args.data_dir, "labels")

    if not os.path.exists(args.metadata_csv):
        raise FileNotFoundError(f"Metadata file not found: {args.metadata_csv}")

    metadata_df = pd.read_csv(args.metadata_csv)
    matched_df = metadata_df[metadata_df["is_matched"] == 1].copy().reset_index(drop=True)

    # 80/20 Deterministic Train/Val Split
    indices = list(range(len(matched_df)))
    random.seed(args.seed)
    random.shuffle(indices)
    split_idx = int(0.8 * len(indices))
    train_idx, val_idx = indices[:split_idx], indices[split_idx:]

    train_items = []
    for idx in train_idx:
        row = matched_df.iloc[idx]
        train_items.append({
            "img_path": os.path.join(images_dir, f"{row['sample_id']}.tif"),
            "mask_path": os.path.join(labels_dir, f"{row['sample_id']}.png"),
            "is_synthetic": False
        })

    val_items = []
    for idx in val_idx:
        row = matched_df.iloc[idx]
        val_items.append({
            "img_path": os.path.join(images_dir, f"{row['sample_id']}.tif"),
            "mask_path": os.path.join(labels_dir, f"{row['sample_id']}.png"),
            "is_synthetic": False
        })

    # Optional: Load Synthetic Dataset
    if args.synthetic_dir and os.path.exists(args.synthetic_dir):
        synth_csv = os.path.join(args.synthetic_dir, "synthetic_metadata.csv")
        synth_imgs = os.path.join(args.synthetic_dir, "images")
        synth_masks = os.path.join(args.synthetic_dir, "labels")
        if os.path.exists(synth_csv):
            synth_df = pd.read_csv(synth_csv)
            for _, row in synth_df.iterrows():
                train_items.append({
                    "img_path": os.path.join(synth_imgs, row["image_filename"]),
                    "mask_path": os.path.join(synth_masks, row["mask_filename"]),
                    "is_synthetic": True
                })
            print(f"Integrated {len(synth_df)} high-fidelity synthetic scenes into training pipeline.")

    print(f"Training dataset size: {len(train_items)} | Validation dataset size: {len(val_items)}")

    use_golden = (args.in_channels == 6)
    train_dataset = MultispectralWaterDataset(train_items, use_golden_subset=use_golden, is_train=True)
    val_dataset = MultispectralWaterDataset(val_items, use_golden_subset=use_golden, is_train=False)

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=2)

    model = MultispectralUNet(in_channels=args.in_channels, out_channels=1, base=32).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-6)
    criterion = CombinedWaterLoss(bce_weight=0.5, dice_weight=0.5)
    scaler = GradScaler("cuda" if torch.cuda.is_available() else "cpu")
    metrics = SegmentationMetrics()

    best_iou = 0.0

    print("=" * 80)
    print("TRAINING MULTISPECTRAL U-NET...")
    print("Epoch | Train Loss | Val Loss | Val IoU  | F1-Score | Status")
    print("=" * 80)

    for epoch in range(1, args.epochs + 1):
        model.train()
        train_loss = 0.0
        for imgs, masks in train_loader:
            imgs, masks = imgs.to(device), masks.to(device)
            optimizer.zero_grad()
            with autocast("cuda" if torch.cuda.is_available() else "cpu"):
                logits = model(imgs)
                loss = criterion(logits, masks)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            train_loss += loss.item() * imgs.size(0)
        scheduler.step()

        model.eval()
        val_loss = 0.0
        metrics.reset()
        with torch.no_grad():
            for imgs, masks in val_loader:
                imgs, masks = imgs.to(device), masks.to(device)
                with autocast("cuda" if torch.cuda.is_available() else "cpu"):
                    logits = model(imgs)
                    loss = criterion(logits, masks)
                val_loss += loss.item() * imgs.size(0)
                metrics.update(logits, masks)

        val_scores = metrics.compute()
        epoch_iou = val_scores["iou"]
        epoch_f1 = val_scores["f1"]

        status = ""
        if epoch_iou > best_iou:
            best_iou = epoch_iou
            torch.save(model.state_dict(), args.output_model)
            status = f"=> Best Model (IoU: {best_iou:.4f})"

        if epoch % 5 == 0 or epoch == 1 or epoch == args.epochs:
            print(f"{epoch:^5} | {train_loss/len(train_items):^10.4f} | {val_loss/len(val_items):^8.4f} | {epoch_iou:^8.4f} | {epoch_f1:^8.4f} | {status}")

    print("=" * 80)
    print(f"TRAINING COMPLETE. Peak Validation IoU: {best_iou:.4f}")
    print(f"Checkpoint saved to: {args.output_model}")
    print("=" * 80)


if __name__ == "__main__":
    main()
