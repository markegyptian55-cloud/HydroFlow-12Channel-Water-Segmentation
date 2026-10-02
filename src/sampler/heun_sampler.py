import torch
import torch.nn as nn


@torch.no_grad()
def sample_flow_heun(
    model: nn.Module,
    masks: torch.Tensor,
    num_steps: int = 25,
    noise_scale: float = 0.98,
    img_channels: int = 6
) -> torch.Tensor:
    """
    Continuous-Time Optimal Transport CFM Sampler using Heun's 2nd-Order Predictor-Corrector Method.
    Solves dx/dt = v_theta(x, t, mask) from t=0 (Gaussian noise) to t=1 (multispectral scene).
    
    Args:
        model: Velocity field network v_theta(x, t, mask).
        masks: Conditioning binary water masks, shape (B, 1, H, W).
        num_steps: Number of integration steps along the continuous trajectory.
        noise_scale: Standard deviation scaling for initial Gaussian noise x_0.
        img_channels: Number of multispectral bands (default 6).
        
    Returns:
        torch.Tensor: Generated multispectral images normalized in [0, 1], shape (B, C, H, W).
    """
    device = masks.device
    B, _, H, W = masks.shape
    dt = 1.0 / num_steps
    
    # Sample from source distribution x_0 ~ N(0, noise_scale^2 * I)
    x = torch.randn((B, img_channels, H, W), device=device) * noise_scale
    
    for step in range(num_steps):
        t_curr = step * dt
        t_batch = torch.full((B,), t_curr, device=device)
        
        # Predictor step
        v1 = model(x, t_batch, masks)
        
        if step < num_steps - 1:
            t_next = (step + 1) * dt
            t_next_batch = torch.full((B,), t_next, device=device)
            x_pred = x + v1 * dt
            
            # Corrector step
            v2 = model(x_pred, t_next_batch, masks)
            x = x + 0.5 * (v1 + v2) * dt
        else:
            x = x + v1 * dt
            
    # Rescale from [-1, 1] to physical normalized bounds [0, 1]
    return torch.clamp((x + 1.0) / 2.0, 0.0, 1.0)
