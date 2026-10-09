"""
Modular CLI script for Fine-Tuning Pretrained ResNet-34 U-Net (12-Band or 6-Band).
Implements the two-phase schedule (Warmup + Full Fine-Tuning) with AMP and Early Stopping.
"""
import os
import random
import argparse
import time
import numpy as np
import pandas as pd
import tifffile as tiff
from PIL import Image
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from torch.amp import GradScaler, autocast
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

from src.models.pretrained_smp import build_pretrained_unet
from src.losses.combined_loss import CombinedWaterLoss
from src.metrics.evaluator import compute_metrics


def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


class S2WaterDataset(Dataset):
    def __init__(self, df, images_dir, labels_dir, band_mins, band_maxs, bands=12, is_train=True):
        self.df = df.reset_index(drop=True)
        self.images_dir = images_dir
        self.labels_dir = labels_dir
        self.band_mins = band_mins
        self.band_maxs = band_maxs
        self.bands = bands
        self.is_train = is_train
        self.golden_indices = [1, 2, 3, 7, 10, 11]

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        sid = str(row["sample_id"])
        img_path = os.path.join(self.images_dir, f"{sid}.tif")
        mask_path = os.path.join(self.labels_dir, f"{sid}.png")

        raw_img = tiff.imread(img_path).astype(np.float32)
        raw_mask = np.array(Image.open(mask_path), dtype=np.float32)

        norm_img = np.zeros((12, 128, 128), dtype=np.float32)
        for b in range(12):
            ch = raw_img[:, :, b]
            ch[ch < -9000] = 0.0
            if b <= 6:
                ch = np.clip(ch, 0.0, None)
            norm_ch = (ch - self.band_mins[b]) / (self.band_maxs[b] - self.band_mins[b] + 1e-6)
            norm_img[b] = np.clip(norm_ch, 0.0, 1.0)

        if self.bands == 6:
            norm_img = norm_img[self.golden_indices, :, :]

        binary_mask = (raw_mask > 0).astype(np.float32)[np.newaxis, :, :]

        img_tensor = torch.from_numpy(norm_img)
        mask_tensor = torch.from_numpy(binary_mask)

        if self.is_train:
            if random.random() > 0.5:
                img_tensor = torch.flip(img_tensor, dims=[-1])
                mask_tensor = torch.flip(mask_tensor, dims=[-1])
            if random.random() > 0.5:
                img_tensor = torch.flip(img_tensor, dims=[-2])
                mask_tensor = torch.flip(mask_tensor, dims=[-2])
            if random.random() > 0.5:
                k = random.choice([1, 2, 3])
                img_tensor = torch.rot90(img_tensor, k, dims=[-2, -1])
                mask_tensor = torch.rot90(mask_tensor, k, dims=[-2, -1])

        return img_tensor, mask_tensor


def main():
    parser = argparse.ArgumentParser(description="Fine-Tune Pretrained ResNet-34 U-Net on Multispectral Data")
    parser.add_argument("--data-root", type=str, default="satalite data", help="Root directory containing images and labels")
    parser.add_argument("--bands", type=int, choices=[6, 12], default=12, help="Number of spectral bands (12 or 6)")
    parser.add_argument("--total-epochs", type=int, default=100, help="Total training epochs")
    parser.add_argument("--warmup-epochs", type=int, default=3, help="Warmup epochs with frozen encoder")
    parser.add_argument("--patience", type=int, default=20, help="Patience epochs for early stopping")
    parser.add_argument("--lr", type=float, default=3e-4, help="Initial learning rate")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    parser.add_argument("--output-dir", type=str, default="checkpoints", help="Output directory for checkpoints")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    set_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    os.makedirs(args.output_dir, exist_ok=True)

    print("=" * 70)
    print("HYDROFLOW TRANSFER LEARNING TRAINING PIPELINE")
    print(f"Device:           {device}")
    print(f"Spectral Bands:   {args.bands} Channels")
    print(f"Total Epochs:     {args.total_epochs} (Warmup: {args.warmup_epochs})")
    print(f"Patience:         {args.patience}")
    print("=" * 70)

    # Resolve paths
    images_dir = os.path.join(args.data_root, "images")
    labels_dir = os.path.join(args.data_root, "labels")
    
    # Discover matched pairs
    image_ids = set(f.replace(".tif", "") for f in os.listdir(images_dir) if f.endswith(".tif"))
    label_ids = set(f.replace(".png", "") for f in os.listdir(labels_dir) if f.endswith(".png"))
    matched_ids = sorted(list(image_ids.intersection(label_ids)))
    
    df_meta = pd.DataFrame({"sample_id": matched_ids})
    
    # Calculate water presence for stratified split
    has_water = []
    for sid in matched_ids:
        m = Image.open(os.path.join(labels_dir, f"{sid}.png"))
        has_water.append(int(np.array(m).max() > 0))
    df_meta["has_water"] = has_water

    # Calibrate robust bounds across all matched scenes
    print(f"Calibrating normalization bounds across {len(matched_ids)} scenes...")
    band_mins = np.zeros(12, dtype=np.float32)
    band_maxs = np.zeros(12, dtype=np.float32)
    
    all_imgs = [tiff.imread(os.path.join(images_dir, f"{sid}.tif")).astype(np.float32) for sid in matched_ids]
    all_arr = np.stack(all_imgs, axis=0)
    for b in range(12):
        b_data = all_arr[:, :, :, b]
        valid = b_data[b_data > -9000]
        if b <= 6:
            valid = np.clip(valid, 0.0, None)
        band_mins[b] = np.percentile(valid, 1) if len(valid) > 0 else 0.0
        band_maxs[b] = np.percentile(valid, 99) if len(valid) > 0 else 1.0
    del all_imgs, all_arr

    # Stratified 80/20 Split
    train_df, val_df = train_test_split(df_meta, test_size=0.20, random_state=args.seed, stratify=df_meta["has_water"])
    print(f"Train set: {len(train_df)} scenes | Validation set: {len(val_df)} scenes")

    # DataLoaders
    train_ds = S2WaterDataset(train_df, images_dir, labels_dir, band_mins, band_maxs, bands=args.bands, is_train=True)
    val_ds = S2WaterDataset(val_df, images_dir, labels_dir, band_mins, band_maxs, bands=args.bands, is_train=False)

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, pin_memory=True)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, pin_memory=True)

    # Build Model
    model = build_pretrained_unet(encoder_name="resnet34", in_channels=args.bands, classes=1).to(device)
    criterion = CombinedWaterLoss().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scaler = GradScaler()

    # Initial Warmup: freeze encoder
    model.freeze_encoder()
    print("Encoder frozen for initial warmup phase.")

    best_val_iou = 0.0
    patience_counter = 0
    history = []
    checkpoint_path = os.path.join(args.output_dir, f"unet_resnet34_{args.bands}ch_best.pth")

    for epoch in range(1, args.total_epochs + 1):
        if epoch == args.warmup_epochs + 1:
            print(f"\n[UNFREEZE] Unfreezing encoder at Epoch {epoch} for full fine-tuning.")
            model.unfreeze_encoder()
            optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr * 0.5, weight_decay=1e-4)
            scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.total_epochs - args.warmup_epochs, eta_min=1e-6)

        # Train loop
        model.train()
        train_loss = 0.0
        for imgs, masks in train_loader:
            imgs, masks = imgs.to(device), masks.to(device)
            optimizer.zero_grad()
            with autocast(device_type="cuda" if torch.cuda.is_available() else "cpu"):
                logits = model(imgs)
                loss = criterion(logits, masks)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            train_loss += loss.item() * imgs.size(0)

        train_loss /= len(train_loader.dataset)

        # Val loop
        model.eval()
        val_loss = 0.0
        val_ious, val_f1s = [], []
        with torch.no_grad():
            for imgs, masks in val_loader:
                imgs, masks = imgs.to(device), masks.to(device)
                logits = model(imgs)
                loss = criterion(logits, masks)
                val_loss += loss.item() * imgs.size(0)
                
                probs = torch.sigmoid(logits)
                preds = (probs > 0.5).float()
                inter = (preds * masks).sum().item()
                union = (preds + masks - (preds * masks)).sum().item()
                val_ious.append(inter / (union + 1e-8))
                p = inter / (preds.sum().item() + 1e-8)
                r = inter / (masks.sum().item() + 1e-8)
                val_f1s.append(2 * p * r / (p + r + 1e-8))

        val_loss /= len(val_loader.dataset)
        val_iou = float(np.mean(val_ious))
        val_f1 = float(np.mean(val_f1s))

        if epoch > args.warmup_epochs and 'scheduler' in locals():
            scheduler.step()

        print(f"Epoch {epoch:03d} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val IoU: {val_iou:.4f} | Val F1: {val_f1:.4f}")

        if val_iou > best_val_iou:
            best_val_iou = val_iou
            patience_counter = 0
            torch.save(model.state_dict(), checkpoint_path)
            print(f"  => Checkpoint saved (IoU: {val_iou:.4f})")
        else:
            if epoch > args.warmup_epochs:
                patience_counter += 1
                if patience_counter >= args.patience:
                    print(f"\n[STOP] Early stopping triggered at epoch {epoch}.")
                    break

    print("=" * 70)
    print(f"Training Complete! Peak Validation IoU: {best_val_iou * 100:.2f}%")
    print(f"Best model weights saved to: {checkpoint_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
