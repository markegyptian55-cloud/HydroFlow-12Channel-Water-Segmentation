import argparse
import os
import shutil
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import tifffile as tiff
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from tqdm.auto import tqdm

from src.models.flow_matching import ConditionalFlowUNet
from src.sampler.heun_sampler import sample_flow_heun
from src.gatekeeper.quality_gatekeeper import QualityGatekeeper
from src.data.dataset import NORM_MIN, NORM_MAX


class OrphanMaskDataset(Dataset):
    def __init__(self, mask_paths):
        self.mask_paths = mask_paths

    def __len__(self):
        return len(self.mask_paths)

    def __getitem__(self, idx):
        path = self.mask_paths[idx]
        mask = Image.open(path).convert('L')
        mask_arr = (np.array(mask, dtype=np.float32) > 0).astype(np.float32)
        mask_chw = np.expand_dims(mask_arr, axis=0)
        return torch.from_numpy(mask_chw), Path(path).stem


def parse_args():
    parser = argparse.ArgumentParser(description="Multi-Seed Generative Data Augmentation for Satellite Imagery")
    parser.add_argument("--checkpoint", type=str, required=True, help="Trained Flow Matching weights (.pth)")
    parser.add_argument("--labels_dir", type=str, required=True, help="Directory containing orphan mask PNGs")
    parser.add_argument("--metadata_csv", type=str, required=True, help="Metadata CSV identifying orphan masks")
    parser.add_argument("--output_dir", type=str, default="synthetic_water_dataset", help="Output directory")
    parser.add_argument("--seeds", type=int, default=7, help="Number of stochastic seeds per orphan mask")
    parser.add_argument("--steps", type=int, default=25, help="Heun ODE solver integration steps")
    parser.add_argument("--noise_scale", type=float, default=0.98, help="Initial noise scale")
    return parser.parse_args()


def main():
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Executing Multi-Seed Generator on: {device}")

    # Load Orphan Masks
    metadata_df = pd.read_csv(args.metadata_csv)
    orphan_df = metadata_df[metadata_df["is_matched"] == 0].copy()
    orphan_paths = [os.path.join(args.labels_dir, f"{row['sample_id']}.png") for _, row in orphan_df.iterrows()
                    if os.path.exists(os.path.join(args.labels_dir, f"{row['sample_id']}.png"))]

    print(f"Found {len(orphan_paths)} orphan masks to evaluate across {args.seeds} stochastic seeds.")
    loader = DataLoader(OrphanMaskDataset(orphan_paths), batch_size=15, shuffle=False)

    # Load Flow Matching Generator
    model = ConditionalFlowUNet(img_channels=6, mask_channels=1, base=48).to(device)
    state_dict = torch.load(args.checkpoint, map_location=device)
    model.load_state_dict(state_dict)
    model.eval()

    gatekeeper = QualityGatekeeper()

    out_dir = Path(args.output_dir)
    imgs_dir = out_dir / "images"
    masks_dir = out_dir / "labels"
    shutil.rmtree(out_dir, ignore_errors=True)
    imgs_dir.mkdir(parents=True, exist_ok=True)
    masks_dir.mkdir(parents=True, exist_ok=True)

    denom_arr = (np.array(NORM_MAX) - np.array(NORM_MIN))[:, None, None]
    norm_min_arr = np.array(NORM_MIN)[:, None, None]

    total_evaluated = 0
    total_accepted = 0
    accepted_records = []

    for seed_idx in range(args.seeds):
        curr_seed = 42 + seed_idx * 137
        torch.manual_seed(curr_seed)
        print(f"\n[Seed Batch {seed_idx + 1}/{args.seeds}] Running Seed: {curr_seed}")

        for masks_batch, sample_ids in tqdm(loader, desc=f"Seed {seed_idx + 1}"):
            masks_batch = masks_batch.to(device)
            B = masks_batch.size(0)

            candidates = sample_flow_heun(model, masks_batch, num_steps=args.steps, noise_scale=args.noise_scale)

            for b in range(B):
                total_evaluated += 1
                synth_01 = candidates[b].cpu().numpy()
                target_mask = masks_batch[b, 0].cpu().numpy().astype(bool)
                sample_id = f"synth_s{seed_idx}_{sample_ids[b]}"

                passed, sep, iou = gatekeeper.evaluate(synth_01, target_mask)
                if passed:
                    total_accepted += 1
                    raw_synth = synth_01 * denom_arr + norm_min_arr
                    raw_synth_hwc = np.transpose(raw_synth, (1, 2, 0)).astype(np.float32)

                    out_img = imgs_dir / f"{sample_id}.tif"
                    out_mask = masks_dir / f"{sample_id}.png"

                    tiff.imwrite(str(out_img), raw_synth_hwc)
                    Image.fromarray((target_mask * 255).astype(np.uint8)).save(str(out_mask))

                    accepted_records.append({
                        "sample_id": sample_id,
                        "image_filename": out_img.name,
                        "mask_filename": out_mask.name,
                        "is_synthetic": 1,
                        "spectral_separation": sep,
                        "consistency_iou": iou,
                        "seed": curr_seed
                    })

    df = pd.DataFrame(accepted_records)
    df.to_csv(out_dir / "synthetic_metadata.csv", index=False)

    print("\n" + "=" * 80)
    print("QUALITY CONTROL SUMMARY:")
    print(f"Total Evaluated: {total_evaluated} | Accepted: {total_accepted} ({total_accepted/max(total_evaluated,1)*100:.1f}%)")
    print(f"Output saved to: {out_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()
