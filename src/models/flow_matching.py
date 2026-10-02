import math
import torch
import torch.nn as nn


class SinusoidalPosEmb(nn.Module):
    """Sinusoidal positional time embeddings for continuous-time conditioning."""
    def __init__(self, dim: int):
        super().__init__()
        self.dim = dim

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        device = x.device
        half_dim = self.dim // 2
        emb = math.log(10000) / (half_dim - 1)
        emb = torch.exp(torch.arange(half_dim, device=device) * -emb)
        emb = x[:, None] * emb[None, :]
        return torch.cat((emb.sin(), emb.cos()), dim=-1)


class TimeConditionedBlock(nn.Module):
    """Double convolution block with injected time embeddings and residual connection."""
    def __init__(self, in_channels: int, out_channels: int, time_emb_dim: int):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1)
        self.norm1 = nn.BatchNorm2d(out_channels)
        self.act1 = nn.ReLU(inplace=True)
        
        self.time_mlp = nn.Sequential(
            nn.Linear(time_emb_dim, out_channels),
            nn.ReLU(inplace=True)
        )
        
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1)
        self.norm2 = nn.BatchNorm2d(out_channels)
        self.act2 = nn.ReLU(inplace=True)
        
        self.residual = nn.Conv2d(in_channels, out_channels, kernel_size=1) if in_channels != out_channels else nn.Identity()

    def forward(self, x: torch.Tensor, t_emb: torch.Tensor) -> torch.Tensor:
        h = self.act1(self.norm1(self.conv1(x)))
        h = h + self.time_mlp(t_emb)[:, :, None, None]
        h = self.act2(self.norm2(self.conv2(h)))
        return h + self.residual(x)


class ConditionalFlowUNet(nn.Module):
    """
    Continuous Normalizing Flow / Optimal Transport CFM Velocity Field Estimator.
    Maps noise x_0 ~ N(0, I) to multispectral satellite distribution x_1 conditioned on water mask c.
    Velocity network: v_theta(x_t, t, c) -> dx/dt
    """
    def __init__(self, img_channels: int = 6, mask_channels: int = 1, base: int = 48, time_dim: int = 128):
        super().__init__()
        self.time_mlp = nn.Sequential(
            SinusoidalPosEmb(time_dim),
            nn.Linear(time_dim, time_dim * 2),
            nn.ReLU(inplace=True),
            nn.Linear(time_dim * 2, time_dim)
        )
        
        in_ch = img_channels + mask_channels
        self.down1 = TimeConditionedBlock(in_ch, base, time_dim)
        self.pool1 = nn.MaxPool2d(2)
        self.down2 = TimeConditionedBlock(base, base * 2, time_dim)
        self.pool2 = nn.MaxPool2d(2)
        self.down3 = TimeConditionedBlock(base * 2, base * 4, time_dim)
        self.pool3 = nn.MaxPool2d(2)
        
        self.mid = TimeConditionedBlock(base * 4, base * 4, time_dim)
        
        self.up3 = nn.ConvTranspose2d(base * 4, base * 2, kernel_size=2, stride=2)
        self.dec3 = TimeConditionedBlock(base * 4, base * 2, time_dim)
        self.up2 = nn.ConvTranspose2d(base * 2, base, kernel_size=2, stride=2)
        self.dec2 = TimeConditionedBlock(base * 2, base, time_dim)
        self.up1 = nn.ConvTranspose2d(base, base, kernel_size=2, stride=2)
        self.dec1 = TimeConditionedBlock(base * 2, base, time_dim)
        
        self.out_conv = nn.Conv2d(base, img_channels, kernel_size=1)

    def forward(self, x: torch.Tensor, t: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        t_emb = self.time_mlp(t)
        inp = torch.cat([x, mask], dim=1)
        
        h1 = self.down1(inp, t_emb)
        d1 = self.pool1(h1)
        h2 = self.down2(d1, t_emb)
        d2 = self.pool2(h2)
        h3 = self.down3(d2, t_emb)
        d3 = self.pool3(h3)
        
        mid = self.mid(d3, t_emb)
        
        u3 = self.up3(mid)
        dec3 = self.dec3(torch.cat([u3, h3], dim=1), t_emb)
        u2 = self.up2(dec3)
        dec2 = self.dec2(torch.cat([u2, h2], dim=1), t_emb)
        u1 = self.up1(dec2)
        dec1 = self.dec1(torch.cat([u1, h1], dim=1), t_emb)
        
        return self.out_conv(dec1)
