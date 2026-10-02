import torch
import torch.nn as nn


class DiceLoss(nn.Module):
    """
    Smooth Differentiable Dice Loss for Binary Water Segmentation.
    L_dice = 1 - (2 * |P * Y| + eps) / (|P| + |Y| + eps)
    """
    def __init__(self, smooth: float = 1e-6):
        super().__init__()
        self.smooth = smooth

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        probs = torch.sigmoid(logits).view(-1)
        targets = targets.view(-1)
        intersection = (probs * targets).sum()
        denominator = probs.sum() + targets.sum()
        return 1.0 - (2.0 * intersection + self.smooth) / (denominator + self.smooth)


class CombinedWaterLoss(nn.Module):
    """
    Weighted combination of Binary Cross Entropy with Logits and Dice Loss.
    Addresses class imbalance in satellite imagery between water and background land.
    """
    def __init__(self, bce_weight: float = 0.5, dice_weight: float = 0.5, smooth: float = 1e-6):
        super().__init__()
        self.bce_weight = bce_weight
        self.dice_weight = dice_weight
        self.bce_fn = nn.BCEWithLogitsLoss()
        self.dice_fn = DiceLoss(smooth=smooth)

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        bce = self.bce_fn(logits, targets)
        dice = self.dice_fn(logits, targets)
        return self.bce_weight * bce + self.dice_weight * dice
