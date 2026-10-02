from typing import Dict, List
import numpy as np
import torch


class SegmentationMetrics:
    """Accumulates and computes binary segmentation evaluation metrics."""
    def __init__(self, threshold: float = 0.5, eps: float = 1e-8):
        self.threshold = threshold
        self.eps = eps
        self.reset()

    def reset(self):
        self.ious: List[float] = []
        self.f1s: List[float] = []
        self.precisions: List[float] = []
        self.recalls: List[float] = []

    def update(self, logits: torch.Tensor, targets: torch.Tensor):
        probs = torch.sigmoid(logits)
        preds = (probs > self.threshold).float()
        
        preds_flat = preds.view(preds.size(0), -1)
        targets_flat = targets.view(targets.size(0), -1)
        
        for b in range(preds_flat.size(0)):
            p = preds_flat[b]
            t = targets_flat[b]
            
            tp = (p * t).sum().item()
            fp = (p * (1.0 - t)).sum().item()
            fn = ((1.0 - p) * t).sum().item()
            
            iou = tp / (tp + fp + fn + self.eps)
            f1 = (2.0 * tp) / (2.0 * tp + fp + fn + self.eps)
            precision = tp / (tp + fp + self.eps)
            recall = tp / (tp + fn + self.eps)
            
            self.ious.append(iou)
            self.f1s.append(f1)
            self.precisions.append(precision)
            self.recalls.append(recall)

    def compute(self) -> Dict[str, float]:
        return {
            "iou": float(np.mean(self.ious)) if self.ious else 0.0,
            "f1": float(np.mean(self.f1s)) if self.f1s else 0.0,
            "precision": float(np.mean(self.precisions)) if self.precisions else 0.0,
            "recall": float(np.mean(self.recalls)) if self.recalls else 0.0,
        }
