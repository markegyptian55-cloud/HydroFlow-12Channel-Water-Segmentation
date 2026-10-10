import os
import torch

# Base directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEIGHTS_PATH = os.path.join(BASE_DIR, "weights", "best_model.pth")
ONNX_WEIGHTS_PATH = os.path.join(BASE_DIR, "weights", "best_model.onnx")
SAMPLES_DIR = os.path.join(BASE_DIR, "static", "samples")
SAMPLES_META_PATH = os.path.join(SAMPLES_DIR, "samples_meta.json")

# Model configuration
BACKBONE = "resnet34"
IN_CHANNELS = 12
CLASSES = 1
THRESHOLD = 0.5
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Physical Sentinel-2 12-Band Calibration Bounds
# Derived from full dataset 1st and 99th percentiles
BAND_MINS = [69.0, 100.0, 233.0, 104.0, 127.0, 14.0, 11.0, 64.0, 17.0, 17.0, 10.0, 0.0]
BAND_MAXS = [941.0, 1143.0, 1733.0, 2478.0, 4046.0, 4453.0, 3761.0, 224.0, 1902.0, 1907.0, 80.0, 98.0]

# Sentinel-2 Multispectral Band Metadata
BAND_NAMES = [
    "B1 (Coastal Aerosol)",
    "B2 (Blue)",
    "B3 (Green)",
    "B4 (Red)",
    "B5 (Vegetation RedEdge 1)",
    "B6 (Vegetation RedEdge 2)",
    "B7 (Vegetation RedEdge 3)",
    "B8 (Near-Infrared NIR)",
    "B8A (Narrow NIR)",
    "B9 (Water Vapour)",
    "B11 (Shortwave Infrared SWIR-1)",
    "B12 (Shortwave Infrared SWIR-2)"
]

# True color RGB band indices (0-indexed): B4 (Red), B3 (Green), B2 (Blue)
RGB_INDICES = [3, 2, 1]

# Server settings
HOST = "0.0.0.0"
PORT = 5000
DEBUG = False
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB max upload
