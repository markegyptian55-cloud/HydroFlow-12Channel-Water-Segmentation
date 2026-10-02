from typing import Tuple
import numpy as np


class QualityGatekeeper:
    """
    Automated 3-Stage Physical & Geometric Quality Gatekeeper for Satellite Image Synthesis.
    Filters candidate scenes to prevent distribution poisoning of downstream segmentation models.
    """
    def __init__(
        self,
        min_variance_std: float = 0.025,
        min_spectral_diff: float = 0.015,
        min_consistency_iou: float = 0.15,
        nir_band_idx: int = 3 # Index 3 in Golden 6-band subset (B8 NIR)
    ):
        self.min_variance_std = min_variance_std
        self.min_spectral_diff = min_spectral_diff
        self.min_consistency_iou = min_consistency_iou
        self.nir_band_idx = nir_band_idx

    @staticmethod
    def compute_iou(mask1: np.ndarray, mask2: np.ndarray) -> float:
        inter = (mask1 & mask2).sum()
        union = (mask1 | mask2).sum()
        if union == 0:
            return 1.0 if inter == 0 else 0.0
        return float(inter / union)

    def evaluate(self, synth_img_01: np.ndarray, target_mask: np.ndarray) -> Tuple[bool, float, float]:
        """
        Evaluate synthetic candidate scene against target binary mask.
        
        Args:
            synth_img_01: Normalized synthetic scene in [0, 1] range, shape (C, H, W).
            target_mask: Target binary water mask (boolean or {0, 1}), shape (H, W).
            
        Returns:
            Tuple: (is_accepted: bool, spectral_diff: float, consistency_iou: float)
        """
        target_mask_bool = target_mask.astype(bool)
        
        # 1. Image Variance / Dynamic Range Filter
        img_std = float(synth_img_01.std())
        if img_std < self.min_variance_std:
            return False, 0.0, 0.0
            
        # 2. NIR Spectral Absorption Filter
        water_px = target_mask_bool
        land_px  = ~target_mask_bool
        
        if water_px.sum() > 20 and land_px.sum() > 20:
            nir_water = float(synth_img_01[self.nir_band_idx, water_px].mean())
            nir_land  = float(synth_img_01[self.nir_band_idx, land_px].mean())
            spectral_diff = abs(nir_land - nir_water)
            
            if spectral_diff < self.min_spectral_diff:
                return False, spectral_diff, 0.0
        else:
            spectral_diff = 0.5
            
        # 3. Geometric Alignment / Spatial Consistency Filter
        nir_band = synth_img_01[self.nir_band_idx]
        if water_px.sum() > 0:
            water_ratio = float(target_mask_bool.mean())
            thresh = float(np.percentile(nir_band, 100.0 * water_ratio))
            pred_water = (nir_band <= thresh)
        else:
            pred_water = np.zeros_like(target_mask_bool)
            
        consistency_iou = self.compute_iou(pred_water, target_mask_bool)
        
        if water_px.sum() > 20 and consistency_iou < self.min_consistency_iou:
            return False, spectral_diff, consistency_iou
            
        return True, spectral_diff, consistency_iou
