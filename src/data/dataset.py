import os
import random
from typing import List, Dict, Optional, Tuple
import numpy as np
import tifffile as tiff
from PIL import Image
import torch
from torch.utils.data import Dataset

# Sentinel-2 Multispectral Band Mappings
# 0: B1 (Coastal Aerosol), 1: B2 (Blue), 2: B3 (Green), 3: B4 (Red)
# 4: B5 (RE1), 5: B6 (RE2), 6: B7 (RE3), 7: B8 (NIR)
# 8: B8A (Narrow NIR), 9: B9 (Water Vapour), 10: B11 (SWIR-1), 11: B12 (SWIR-2)
GOLDEN_BAND_INDICES = [1, 2, 3, 7, 10, 11] # B2, B3, B4, B8, B11, B12

# Calibrated min-max bounds for the 6 Golden Bands across dataset
NORM_MIN = [143.0, 307.0, 204.0, 64.0, 10.0, 0.0]
NORM_MAX = [1299.0, 1946.0, 2642.0, 192.0, 80.0, 94.0]


class MultispectralWaterDataset(Dataset):
    """
    Multispectral Sentinel-2 Water Segmentation Dataset.
    Supports 12-band full scenes, 6-band Golden subset, real and synthetic images,
    and online geometric augmentations.
    """
    def __init__(
        self,
        items: List[Dict[str, any]],
        use_golden_subset: bool = True,
        is_train: bool = True,
        norm_min: Optional[List[float]] = None,
        norm_max: Optional[List[float]] = None
    ):
        self.items = items
        self.use_golden_subset = use_golden_subset
        self.is_train = is_train
        
        n_bands = 6 if use_golden_subset else 12
        min_vals = norm_min if norm_min is not None else (NORM_MIN if use_golden_subset else [0.0] * 12)
        max_vals = norm_max if norm_max is not None else (NORM_MAX if use_golden_subset else [4000.0] * 12)
        
        self.norm_min = np.array(min_vals, dtype=np.float32).reshape(n_bands, 1, 1)
        self.norm_max = np.array(max_vals, dtype=np.float32).reshape(n_bands, 1, 1)
        self.denom = np.where((self.norm_max - self.norm_min) == 0, 1.0, self.norm_max - self.norm_min)

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        item = self.items[idx]
        is_synthetic = item.get('is_synthetic', False)
        
        # Load Multispectral Image (TIFF)
        raw_img = tiff.imread(item['img_path']).astype(np.float32)
        
        # Adjust dimensions to Channel-First (C, H, W)
        if raw_img.ndim == 3 and raw_img.shape[-1] in (6, 12):
            raw_img = np.transpose(raw_img, (2, 0, 1))
            
        if self.use_golden_subset and not is_synthetic and raw_img.shape[0] == 12:
            img_chw = raw_img[GOLDEN_BAND_INDICES, :, :]
        else:
            img_chw = raw_img
            
        # Physical Min-Max Scaling to [0, 1]
        norm_img = np.clip((img_chw - self.norm_min) / self.denom, 0.0, 1.0)
        
        # Load Binary Water Mask (PNG)
        mask = Image.open(item['mask_path']).convert('L')
        mask_arr = (np.array(mask, dtype=np.float32) > 0).astype(np.float32)
        mask_chw = np.expand_dims(mask_arr, axis=0)
        
        # Online Geometric Augmentations during Training
        if self.is_train:
            if random.random() > 0.5:
                norm_img = np.flip(norm_img, axis=2).copy()
                mask_chw = np.flip(mask_chw, axis=2).copy()
            if random.random() > 0.5:
                norm_img = np.flip(norm_img, axis=1).copy()
                mask_chw = np.flip(mask_chw, axis=1).copy()
            k_rot = random.choice([0, 1, 2, 3])
            if k_rot > 0:
                norm_img = np.rot90(norm_img, k=k_rot, axes=(1, 2)).copy()
                mask_chw = np.rot90(mask_chw, k=k_rot, axes=(1, 2)).copy()

        return torch.from_numpy(norm_img), torch.from_numpy(mask_chw)
