import torch
import torch.nn as nn
from typing import Dict, Any, Tuple
import segmentation_models_pytorch as smp


class PretrainedSMPUNet(nn.Module):
    """
    Transfer Learning U-Net with Pretrained ResNet Backbone from segmentation-models-pytorch.
    Supports native multispectral input adaptation (e.g., 12 bands or 6 bands).
    """
    def __init__(
        self,
        encoder_name: str = "resnet34",
        encoder_weights: str = "imagenet",
        in_channels: int = 12,
        classes: int = 1,
        activation: str = None
    ):
        super().__init__()
        self.encoder_name = encoder_name
        self.encoder_weights = encoder_weights
        self.in_channels = in_channels
        self.classes = classes
        
        # Instantiate SMP U-Net with adapted input channels
        self.model = smp.Unet(
            encoder_name=encoder_name,
            encoder_weights=encoder_weights,
            in_channels=in_channels,
            classes=classes,
            activation=activation
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)

    def freeze_encoder(self):
        """Freezes all backbone encoder parameters for the initial warmup phase."""
        for param in self.model.encoder.parameters():
            param.requires_grad = False
        # Ensure the adapted first convolutional layer remains trainable during warmup
        if hasattr(self.model.encoder, "conv1"):
            for param in self.model.encoder.conv1.parameters():
                param.requires_grad = True
        elif hasattr(self.model.encoder, "_conv_stem"):
            for param in self.model.encoder._conv_stem.parameters():
                param.requires_grad = True

    def unfreeze_encoder(self):
        """Unfreezes all backbone encoder parameters for full fine-tuning."""
        for param in self.model.encoder.parameters():
            param.requires_grad = True

    def get_parameter_summary(self) -> Dict[str, Any]:
        """Returns parameter count inventory for encoder, decoder, and total model."""
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        encoder_params = sum(p.numel() for p in self.model.encoder.parameters())
        decoder_params = sum(p.numel() for p in self.model.decoder.parameters())
        
        return {
            "total_params": total_params,
            "trainable_params": trainable_params,
            "encoder_params": encoder_params,
            "decoder_params": decoder_params,
            "encoder_ratio_pct": (encoder_params / total_params) * 100,
            "first_layer_shape": tuple(self.model.encoder.conv1.weight.shape)
            if hasattr(self.model.encoder, "conv1") else None
        }


def build_pretrained_unet(
    encoder_name: str = "resnet34",
    encoder_weights: str = "imagenet",
    in_channels: int = 12,
    classes: int = 1
) -> PretrainedSMPUNet:
    """Convenience builder function for pretrained transfer learning models."""
    return PretrainedSMPUNet(
        encoder_name=encoder_name,
        encoder_weights=encoder_weights,
        in_channels=in_channels,
        classes=classes
    )
