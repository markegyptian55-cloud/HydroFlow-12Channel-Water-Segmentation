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

BAND_NAMES = [
    "Band 0: Coastal / Aerosol",
    "Band 1: Blue",
    "Band 2: Green",
    "Band 3: Red",
    "Band 4: NIR (Water Absorption)",
    "Band 5: SWIR 1",
    "Band 6: SWIR 2",
    "Band 7: QA_PIXEL Bitmask",
    "Band 8: Auxiliary / Thermal IR",
    "Band 9: Water Vapour / Thermal",
    "Band 10: ESA WorldCover LULC (80=Water)",
    "Band 11: JRC Water Occurrence (0-100%)"
]

# True color RGB band indices (0-indexed): B4 (Red), B3 (Green), B2 (Blue)
RGB_INDICES = [3, 2, 1]

# Server settings
HOST = "0.0.0.0"
PORT = 5000
DEBUG = False
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB max upload
