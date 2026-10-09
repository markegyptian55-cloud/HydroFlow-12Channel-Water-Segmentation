"""
Modular CLI evaluation script for Multispectral Water Segmentation models.
Evaluates model checkpoints across unseen validation scenes and computes pixel-level confusion matrices.
"""
import os
import argparse
import numpy as np
import pandas as pd
import tifffile as tiff
from PIL import Image
import torch
from torch.utils.data import DataLoader, Dataset
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split

from src.models.unet import MultispectralUNet
from src.models.pretrained_smp import build_pretrained_unet


class S2EvalDataset(Dataset):
    def __init__(self, df, images_dir, labels_dir, band_mins, band_maxs, bands=12):
        self.df = df.reset_index(drop=True)
        self.images_dir = images_dir
        self.labels_dir = labels_dir
        self.band_mins = band_mins
        self.band_maxs = band_maxs
        self.bands = bands
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
        return torch.from_numpy(norm_img), torch.from_numpy(binary_mask)


def evaluate_checkpoint(checkpoint_path: str, model_type: str, bands: int, data_root: str = "satalite data"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    images_dir = os.path.join(data_root, "images")
    labels_dir = os.path.join(data_root, "labels")

    image_ids = set(f.replace(".tif", "") for f in os.listdir(images_dir) if f.endswith(".tif"))
    label_ids = set(f.replace(".png", "") for f in os.listdir(labels_dir) if f.endswith(".png"))
    matched_ids = sorted(list(image_ids.intersection(label_ids)))

    df_meta = pd.DataFrame({"sample_id": matched_ids})
    has_water = [int(np.array(Image.open(os.path.join(labels_dir, f"{sid}.png"))).max() > 0) for sid in matched_ids]
    df_meta["has_water"] = has_water

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

    _, val_df = train_test_split(df_meta, test_size=0.20, random_state=42, stratify=df_meta["has_water"])
    val_ds = S2EvalDataset(val_df, images_dir, labels_dir, band_mins, band_maxs, bands=bands)
    val_loader = DataLoader(val_ds, batch_size=16, shuffle=False)

    if model_type == "scratch":
        model = MultispectralUNet(in_channels=bands, out_channels=1).to(device)
    else:
        model = build_pretrained_unet(encoder_name="resnet34", in_channels=bands, classes=1).to(device)

    chk = torch.load(checkpoint_path, map_location=device, weights_only=True)
    if isinstance(chk, dict) and "model_state_dict" in chk:
        model.load_state_dict(chk["model_state_dict"])
    else:
        model.load_state_dict(chk)
    model.eval()

    all_preds, all_targets, sample_ious = [], [], []
    with torch.no_grad():
        for imgs, masks in val_loader:
            imgs = imgs.to(device)
            logits = model(imgs)
            preds = (torch.sigmoid(logits) > 0.5).squeeze(1).cpu().numpy().astype(bool)
            targets = masks.squeeze(1).numpy().astype(bool)

            for p, t in zip(preds, targets):
                inter = (p & t).sum()
                u = (p | t).sum()
                sample_ious.append(1.0 if u == 0 else float(inter / u))
                all_preds.append(p.flatten())
                all_targets.append(t.flatten())

    all_preds = np.concatenate(all_preds)
    all_targets = np.concatenate(all_targets)

    cm = confusion_matrix(all_targets, all_preds)
    tn, fp, fn, tp = cm.ravel()

    global_iou = tp / (tp + fp + fn + 1e-8)
    precision = tp / (tp + fp + 1e-8)
    recall = tp / (tp + fn + 1e-8)
    f1 = (2.0 * precision * recall) / (precision + recall + 1e-8)

    print("=" * 65)
    print(f"EVALUATION REPORT: {checkpoint_path}")
    print(f"Architecture:      {model_type.upper()} ({bands} Channels)")
    print(f"Validation Scenes: {len(val_df)} scenes ({len(all_targets):,} pixels)")
    print("-" * 65)
    print(f"True Positives:    {tp:,} pixels")
    print(f"True Negatives:    {tn:,} pixels")
    print(f"False Positives:   {fp:,} pixels")
    print(f"False Negatives:   {fn:,} pixels")
    print("-" * 65)
    print(f"Global Pixel IoU:  {global_iou * 100:.2f}%")
    print(f"Mean Sample IoU:   {np.mean(sample_ious) * 100:.2f}%")
    print(f"Precision:         {precision * 100:.2f}%")
    print(f"Recall:            {recall * 100:.2f}%")
    print(f"F1-Score (Dice):   {f1 * 100:.2f}%")
    print("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Multispectral Water Segmentation Checkpoint")
    parser.add_argument("--checkpoint", type=str, required=True, help="Path to .pth checkpoint file")
    parser.add_argument("--model-type", type=str, choices=["scratch", "pretrained"], default="pretrained", help="Model family")
    parser.add_argument("--bands", type=int, choices=[6, 12], default=12, help="Number of spectral bands")
    parser.add_argument("--data-root", type=str, default="satalite data", help="Root data folder")
    args = parser.parse_args()

    evaluate_checkpoint(args.checkpoint, args.model_type, args.bands, args.data_root)
