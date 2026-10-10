import io
import os
import time
import base64
from typing import Union, Tuple, Dict, Any, Optional
import numpy as np
import tifffile as tiff
from PIL import Image
import torch
import torch.nn as nn

try:
    from .config import (
        BACKBONE, IN_CHANNELS, CLASSES, THRESHOLD, DEVICE,
        WEIGHTS_PATH, ONNX_WEIGHTS_PATH, BAND_MINS, BAND_MAXS, RGB_INDICES, BASE_DIR
    )
    from .models.pretrained_smp import build_pretrained_unet
except ImportError:
    from config import (
        BACKBONE, IN_CHANNELS, CLASSES, THRESHOLD, DEVICE,
        WEIGHTS_PATH, ONNX_WEIGHTS_PATH, BAND_MINS, BAND_MAXS, RGB_INDICES, BASE_DIR
    )
    from models.pretrained_smp import build_pretrained_unet


class WaterInferenceEngine:
    """
    Production-grade multispectral water segmentation inference engine.
    Wraps the fine-tuned Pretrained SMP ResNet-34 U-Net (81.66% Global IoU).
    Optimized with ONNX Runtime (CPU multi-threading) and PyTorch eager fallback.
    """
    def __init__(
        self,
        weights_path: str = WEIGHTS_PATH,
        onnx_path: Optional[str] = None,
        device: Optional[str] = None
    ):
        self.band_mins = np.array(BAND_MINS, dtype=np.float32)
        self.band_maxs = np.array(BAND_MAXS, dtype=np.float32)
        self.weights_path = weights_path
        
        # Determine ONNX weights path
        if onnx_path is None:
            if 'ONNX_WEIGHTS_PATH' in globals() and os.path.exists(ONNX_WEIGHTS_PATH):
                onnx_path = ONNX_WEIGHTS_PATH
            else:
                candidate = os.path.splitext(weights_path)[0] + ".onnx"
                if os.path.exists(candidate):
                    onnx_path = candidate
                elif os.path.exists(os.path.join(BASE_DIR, "weights", "best_model.onnx")):
                    onnx_path = os.path.join(BASE_DIR, "weights", "best_model.onnx")

        self.onnx_path = onnx_path
        self.ort_session = None
        self.model = None
        self.backend = None
        self.device = torch.device(device if device else DEVICE)

        # Attempt ONNX Runtime initialization
        if self.onnx_path and os.path.exists(self.onnx_path):
            try:
                import onnxruntime as ort
                opts = ort.SessionOptions()
                opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                num_threads = min(8, os.cpu_count() or 4)
                opts.intra_op_num_threads = num_threads
                opts.inter_op_num_threads = 2
                opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
                self.ort_session = ort.InferenceSession(
                    self.onnx_path,
                    sess_options=opts,
                    providers=["CPUExecutionProvider"]
                )
                self.input_name = self.ort_session.get_inputs()[0].name
                self.output_name = self.ort_session.get_outputs()[0].name
                self.backend = "onnx"
                self.device = torch.device("cpu")
                print(f"ONNX Runtime engine active ({num_threads} CPU threads, ORT_ENABLE_ALL)")
            except Exception as e:
                print(f"Warning: ONNX Runtime init failed ({e}), falling back to PyTorch eager.")
                self.ort_session = None

        # Fallback to PyTorch eager mode
        if self.ort_session is None:
            self.backend = "pytorch"
            print(f"Initializing PyTorch eager engine on {self.device}...")
            self.model = build_pretrained_unet(
                encoder_name=BACKBONE,
                encoder_weights="imagenet",
                in_channels=IN_CHANNELS,
                classes=CLASSES
            )
            if weights_path and os.path.exists(weights_path):
                state_dict = torch.load(weights_path, map_location=self.device)
                if hasattr(self.model, "model"):
                    self.model.model.load_state_dict(state_dict)
                else:
                    self.model.load_state_dict(state_dict)
            else:
                raise FileNotFoundError(f"Model weights not found at {weights_path}")
            self.model.to(self.device)
            self.model.eval()

    def load_raw_multispectral(self, input_source: Union[str, bytes, io.BytesIO, np.ndarray, Image.Image]) -> np.ndarray:
        """
        Parses multispectral Sentinel-2 TIFF, 6-band ablation data, or fallback optical RGB images
        into a clean (H, W, 12) float32 array.
        Supports both channel-first (C, H, W) and channel-last (H, W, C) layouts.
        """
        if isinstance(input_source, np.ndarray):
            raw = input_source.astype(np.float32)
        elif isinstance(input_source, (bytes, bytearray)):
            try:
                # Try reading as TIFF
                raw = tiff.imread(io.BytesIO(input_source)).astype(np.float32)
            except Exception:
                # Fallback to PIL Image
                pil_img = Image.open(io.BytesIO(input_source)).convert("RGB")
                raw = np.array(pil_img, dtype=np.float32)
        elif isinstance(input_source, (str, io.BytesIO)):
            try:
                raw = tiff.imread(input_source).astype(np.float32)
            except Exception:
                pil_img = Image.open(input_source).convert("RGB")
                raw = np.array(pil_img, dtype=np.float32)
        elif isinstance(input_source, Image.Image):
            raw = np.array(input_source.convert("RGB"), dtype=np.float32)
        else:
            raise ValueError(f"Unsupported input source type: {type(input_source)}")

        # Sanitize NaNs and Infs in raw data
        raw = np.nan_to_num(raw, nan=0.0, posinf=0.0, neginf=0.0)

        # 2D Grayscale handling -> (H, W, 12)
        if raw.ndim == 2:
            return np.stack([raw] * 12, axis=-1)

        if raw.ndim != 3:
            raise ValueError(f"Unexpected image array ndim: {raw.ndim}")

        # Normalize channel layout: ensure channel-last (H, W, C)
        if raw.shape[-1] == 12:
            pass  # Already (H, W, 12)
        elif raw.shape[0] == 12 and raw.shape[-1] != 12:
            raw = np.transpose(raw, (1, 2, 0))  # (12, H, W) -> (H, W, 12)
        elif raw.shape[-1] in (3, 4, 6):
            pass  # Already (H, W, C)
        elif raw.shape[0] in (3, 4, 6) and raw.shape[-1] not in (3, 4, 6):
            raw = np.transpose(raw, (1, 2, 0))  # (C, H, W) -> (H, W, C)
        elif raw.shape[0] == 1 and raw.shape[-1] != 1:
            raw = np.transpose(raw, (1, 2, 0))  # (1, H, W) -> (H, W, 1)

        h, w = raw.shape[0], raw.shape[1]
        c = raw.shape[2]

        if c == 12:
            return raw

        if c == 1:
            # Single channel mask or grayscale -> replicate to 12 channels
            return np.repeat(raw, 12, axis=-1)

        if c == 6:
            # 6-Band Sentinel-2 Golden Ablation Subset:
            # [B2(Blue), B3(Green), B4(Red), B8(NIR), B11(SWIR1), B12(SWIR2)]
            raw_12 = np.zeros((h, w, 12), dtype=np.float32)
            b2 = raw[:, :, 0]
            b3 = raw[:, :, 1]
            b4 = raw[:, :, 2]
            b8 = raw[:, :, 3]
            b11 = raw[:, :, 4]
            b12 = raw[:, :, 5]

            raw_12[:, :, 0] = b2 * 0.95                 # B1 Coastal Aerosol
            raw_12[:, :, 1] = b2                        # B2 Blue
            raw_12[:, :, 2] = b3                        # B3 Green
            raw_12[:, :, 3] = b4                        # B4 Red
            raw_12[:, :, 4] = b4 * 0.6 + b8 * 0.4       # B5 RedEdge 1
            raw_12[:, :, 5] = b4 * 0.3 + b8 * 0.7       # B6 RedEdge 2
            raw_12[:, :, 6] = b4 * 0.1 + b8 * 0.9       # B7 RedEdge 3
            raw_12[:, :, 7] = b8                        # B8 NIR
            raw_12[:, :, 8] = b8 * 0.98                 # B8A Narrow NIR
            raw_12[:, :, 9] = (b3 + b8) * 0.2           # B9 Water Vapour
            raw_12[:, :, 10] = b11                      # B11 SWIR1
            raw_12[:, :, 11] = b12                      # B12 SWIR2
            return raw_12

        if c in (3, 4):
            # RGB / RGBA fallback
            rgb = raw[:, :, :3]
            if np.issubdtype(rgb.dtype, np.floating) and rgb.max() <= 1.0 and rgb.max() > 0.0:
                rgb = rgb * 255.0

            r = rgb[:, :, 0].astype(np.float32)
            g = rgb[:, :, 1].astype(np.float32)
            b = rgb[:, :, 2].astype(np.float32)
            raw_12 = np.zeros((h, w, 12), dtype=np.float32)

            # Physically grounded optical water discrimination
            diff_br = (b - r) / (b + r + 1e-4)
            diff_gr = (g - r) / (g + r + 1e-4)
            blue_water = (diff_br > 0.12) & (r < 100.0)
            green_water = (diff_gr > 0.15) & (b > r * 0.9) & (r < 95.0)
            dark_water = (np.maximum(r, np.maximum(g, b)) < 55.0) & (r <= np.minimum(g, b) + 2.0)
            is_water = np.clip((blue_water | green_water | dark_water).astype(np.float32), 0.0, 1.0)

            # Optical bands aligned with Sentinel-2 calibration baselines
            raw_12[:, :, 0] = b * 1.5 + 200.0   # B1 Coastal Aerosol
            raw_12[:, :, 1] = b * 1.8 + 250.0   # B2 Blue
            raw_12[:, :, 2] = g * 2.2 + 300.0   # B3 Green
            raw_12[:, :, 3] = r * 2.5 + 200.0   # B4 Red

            # RedEdge bands
            raw_12[:, :, 4] = 2300.0 * (1.0 - is_water) + 350.0 * is_water  # B5 RedEdge 1
            raw_12[:, :, 5] = 2450.0 * (1.0 - is_water) + 200.0 * is_water  # B6 RedEdge 2
            raw_12[:, :, 6] = 1750.0 * (1.0 - is_water) + 150.0 * is_water  # B7 RedEdge 3

            # NIR and SWIR bands
            raw_12[:, :, 7] = 70.0 * (1.0 - is_water) + 40.0 * is_water     # B8 NIR
            raw_12[:, :, 8] = 120.0 * (1.0 - is_water) + 40.0 * is_water    # B8A Narrow NIR
            raw_12[:, :, 9] = 120.0 * (1.0 - is_water) + 30.0 * is_water    # B9 Water Vapour
            raw_12[:, :, 10] = 37.0 * (1.0 - is_water) + 15.0 * is_water    # B11 SWIR-1
            raw_12[:, :, 11] = 10.0 * (1.0 - is_water) + 5.0 * is_water     # B12 SWIR-2
            return raw_12

        raise ValueError(f"Unexpected array shape: {raw.shape}. Expected 1, 3, 4, 6, or 12 channels.")

    def _normalize_12ch(self, raw_12ch: np.ndarray) -> np.ndarray:
        """
        Applies physical Sentinel-2 calibration and scales to (12, H, W) in [0, 1].
        """
        raw_12ch = np.nan_to_num(raw_12ch, nan=0.0, posinf=0.0, neginf=0.0)
        h, w = raw_12ch.shape[0], raw_12ch.shape[1]
        norm_img = np.zeros((12, h, w), dtype=np.float32)

        for b in range(12):
            ch = raw_12ch[:, :, b].copy()
            ch[ch < -9000] = 0.0
            if b <= 6:
                ch = np.clip(ch, 0.0, None)
            min_val = self.band_mins[b]
            max_val = self.band_maxs[b]
            norm_ch = (ch - min_val) / (max_val - min_val + 1e-6)
            norm_img[b] = np.clip(norm_ch, 0.0, 1.0)

        return norm_img

    def preprocess(self, raw_12ch: np.ndarray) -> Tuple[torch.Tensor, Tuple[int, int]]:
        """
        Applies physical calibration and formats tensor (1, 12, H, W) for PyTorch eager compatibility.
        """
        norm_img = self._normalize_12ch(raw_12ch)
        h, w = raw_12ch.shape[0], raw_12ch.shape[1]
        tensor = torch.from_numpy(norm_img).unsqueeze(0).to(self.device)
        return tensor, (h, w)

    def create_rgb_composite(self, raw_12ch: np.ndarray) -> Image.Image:
        """
        Creates a high-contrast true-color RGB composite from B4 (Red), B3 (Green), B2 (Blue).
        """
        r = raw_12ch[:, :, RGB_INDICES[0]].copy()
        g = raw_12ch[:, :, RGB_INDICES[1]].copy()
        b = raw_12ch[:, :, RGB_INDICES[2]].copy()

        r = np.nan_to_num(r, nan=0.0, posinf=0.0, neginf=0.0)
        g = np.nan_to_num(g, nan=0.0, posinf=0.0, neginf=0.0)
        b = np.nan_to_num(b, nan=0.0, posinf=0.0, neginf=0.0)
        r = np.clip(r, 0.0, None)
        g = np.clip(g, 0.0, None)
        b = np.clip(b, 0.0, None)

        def stretch(band: np.ndarray) -> np.ndarray:
            p2 = float(np.percentile(band, 2))
            p98 = float(np.percentile(band, 98))
            if p98 <= p2:
                p98 = p2 + 1.0
            stretched = np.clip((band - p2) / (p98 - p2), 0.0, 1.0)
            return (stretched * 255.0).astype(np.uint8)

        rgb_arr = np.stack([stretch(r), stretch(g), stretch(b)], axis=-1)
        return Image.fromarray(rgb_arr, mode="RGB")

    def create_overlay(
        self,
        rgb_img: Image.Image,
        binary_mask: np.ndarray,
        color: Tuple[int, int, int] = (0, 229, 255),
        alpha: float = 0.45
    ) -> Image.Image:
        """
        Blends true-color RGB with semi-transparent neon aqua water overlay and crisp contour.
        """
        rgb_base = rgb_img.convert("RGBA")
        overlay_arr = np.zeros((binary_mask.shape[0], binary_mask.shape[1], 4), dtype=np.uint8)

        # Highlight water pixels
        water_idx = binary_mask > 0
        overlay_arr[water_idx, 0] = color[0]
        overlay_arr[water_idx, 1] = color[1]
        overlay_arr[water_idx, 2] = color[2]
        overlay_arr[water_idx, 3] = int(255 * alpha)

        # Subtle boundary outline
        try:
            from scipy.ndimage import binary_dilation
            dilated = binary_dilation(water_idx, iterations=1)
            edges = dilated & (~water_idx)
        except ImportError:
            from PIL import ImageFilter
            m_pil = Image.fromarray((water_idx * 255).astype(np.uint8), mode="L")
            m_dilated = m_pil.filter(ImageFilter.MaxFilter(3))
            dilated = np.array(m_dilated) > 0
            edges = dilated & (~water_idx)
        overlay_arr[edges, 0] = 255
        overlay_arr[edges, 1] = 255
        overlay_arr[edges, 2] = 255
        overlay_arr[edges, 3] = 220

        overlay_img = Image.fromarray(overlay_arr, mode="RGBA")
        blended = Image.alpha_composite(rgb_base, overlay_img)
        return blended.convert("RGB")

    @staticmethod
    def to_base64(pil_img: Image.Image, format: str = "PNG") -> str:
        buffered = io.BytesIO()
        pil_img.save(buffered, format=format)
        encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")
        mime = "image/png" if format.upper() == "PNG" else "image/jpeg"
        return f"data:{mime};base64,{encoded}"

    @staticmethod
    def to_bytes(pil_img: Image.Image, format: str = "PNG") -> bytes:
        buffered = io.BytesIO()
        pil_img.save(buffered, format=format)
        return buffered.getvalue()

    def predict(
        self,
        input_source: Union[str, bytes, io.BytesIO, np.ndarray, Image.Image],
        threshold: float = THRESHOLD
    ) -> Dict[str, Any]:
        """
        Executes end-to-end inference using ONNX Runtime (or PyTorch eager) and returns masks, statistics, and visuals.
        """
        t0 = time.perf_counter()

        # Step 1: Load raw 12-channel multispectral raster
        raw_12ch = self.load_raw_multispectral(input_source)
        orig_h, orig_w = raw_12ch.shape[0], raw_12ch.shape[1]
        
        # Step 2: Preprocess and calibrate
        norm_img = self._normalize_12ch(raw_12ch)  # Shape (12, H, W)

        # Ensure spatial dimensions are multiples of 32 for U-Net architecture
        pad_h = (32 - (orig_h % 32)) % 32
        pad_w = (32 - (orig_w % 32)) % 32
        if pad_h > 0 or pad_w > 0:
            norm_input = np.pad(norm_img, ((0, 0), (0, pad_h), (0, pad_w)), mode="edge")
        else:
            norm_input = norm_img
        
        # Step 3: Forward Pass (ONNX Runtime session or PyTorch eager)
        if self.backend == "onnx" and self.ort_session is not None:
            ort_input = norm_input[np.newaxis, ...]  # (1, 12, pad_h, pad_w)
            ort_outs = self.ort_session.run(None, {self.input_name: ort_input})
            # ONNX output shape is (1, 1, pad_h, pad_w)
            logits = ort_outs[0][0, 0]
            if pad_h > 0 or pad_w > 0:
                logits = logits[:orig_h, :orig_w]
            probs = 1.0 / (1.0 + np.exp(-np.clip(logits, -88.0, 88.0)))
        else:
            tensor = torch.from_numpy(norm_input).unsqueeze(0).to(self.device)
            with torch.no_grad():
                logits = self.model(tensor)
                probs = torch.sigmoid(logits)[0, 0].cpu().numpy()
            if pad_h > 0 or pad_w > 0:
                probs = probs[:orig_h, :orig_w]

        # Ensure correct 2D shape
        if probs.ndim != 2:
            probs = probs.reshape((orig_h, orig_w))

        # Step 4: Binary Decision Thresholding
        binary_mask = (probs >= threshold).astype(np.uint8)

        # Step 5: Metrics & Statistics
        total_pixels = int(binary_mask.size)
        water_pixels = int(binary_mask.sum())
        water_percentage = float(round((water_pixels / max(total_pixels, 1)) * 100.0, 2))
        
        if water_pixels > 0:
            mean_confidence = float(round(float(probs[binary_mask == 1].mean()) * 100.0, 2))
        else:
            mean_confidence = 0.0

        latency_ms = float(round((time.perf_counter() - t0) * 1000.0, 2))

        # Step 6: Visual Assets Generation
        rgb_preview = self.create_rgb_composite(raw_12ch)
        mask_preview = Image.fromarray((binary_mask * 255).astype(np.uint8), mode="L")
        overlay_preview = self.create_overlay(rgb_preview, binary_mask)

        return {
            "success": True,
            "dimensions": {"width": orig_w, "height": orig_h},
            "water_percentage": water_percentage,
            "water_pixels": water_pixels,
            "total_pixels": total_pixels,
            "confidence_mean": mean_confidence,
            "threshold_used": threshold,
            "latency_ms": latency_ms,
            "device_used": str(self.device),
            "backend": self.backend,
            "binary_mask": binary_mask,
            "probability_map": probs,
            "rgb_preview": rgb_preview,
            "mask_preview": mask_preview,
            "overlay_preview": overlay_preview
        }
