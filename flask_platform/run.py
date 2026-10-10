#!/usr/bin/env python3
"""
HydroFlow Platform Launcher.
Starts the Flask server for multispectral water segmentation.
Usage:
    python run.py
"""
import sys
import os

# Ensure current directory is on python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from config import HOST, PORT, DEBUG, DEVICE
from app import app

if __name__ == "__main__":
    print("=" * 70)
    print("  HYDROFLOW MULTISPECTRAL WATER SEGMENTATION PLATFORM")
    print("=" * 70)
    print(f"  * Architecture:      ResNet-34 SMP U-Net (12-Band Pretrained)")
    print(f"  * Global IoU:        81.66% Benchmark (Peak Val: 82.10%)")
    print(f"  * Active Device:     {DEVICE.upper()}")
    print(f"  * Local Web UI:      http://127.0.0.1:{PORT}")
    print(f"  * REST API Docs:     http://127.0.0.1:{PORT}/docs")
    print(f"  * Health Check:      http://127.0.0.1:{PORT}/health")
    print(f"  * Validation Presets:http://127.0.0.1:{PORT}/samples")
    print("=" * 70)
    print("  Press Ctrl+C to stop the platform server.")
    print("=" * 70)
    app.run(host=HOST, port=PORT, debug=DEBUG)
