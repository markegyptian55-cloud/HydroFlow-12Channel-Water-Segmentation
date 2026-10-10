import os
import io
import json
import math
import time
import threading
from collections import OrderedDict
from typing import Dict, Any, Tuple, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from flask import Flask, request, jsonify, send_file, render_template, Response
from flask_cors import CORS
from PIL import Image
import numpy as np

try:
    from .config import (
        HOST, PORT, DEBUG, MAX_CONTENT_LENGTH,
        SAMPLES_DIR, SAMPLES_META_PATH, BACKBONE,
        IN_CHANNELS, CLASSES, THRESHOLD, DEVICE
    )
    from .inference import WaterInferenceEngine
except ImportError:
    from config import (
        HOST, PORT, DEBUG, MAX_CONTENT_LENGTH,
        SAMPLES_DIR, SAMPLES_META_PATH, BACKBONE,
        IN_CHANNELS, CLASSES, THRESHOLD, DEVICE
    )
    from inference import WaterInferenceEngine

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
CORS(app)

# Singleton HTTP session with connection pooling and keep-alive
http_session = requests.Session()
adapter = HTTPAdapter(
    pool_connections=20,
    pool_maxsize=50,
    max_retries=Retry(total=2, backoff_factor=0.2, status_forcelist=[500, 502, 503, 504])
)
http_session.mount("https://", adapter)
http_session.mount("http://", adapter)


# Thread-safe in-memory LRU tile cache
class LRUTileCache:
    """Thread-safe OrderedDict-based LRU tile cache for satellite imagery."""
    def __init__(self, maxsize: int = 128):
        self.maxsize = maxsize
        self.cache = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: Tuple) -> Optional[Image.Image]:
        with self._lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                return self.cache[key]
            return None

    def put(self, key: Tuple, value: Image.Image):
        with self._lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.maxsize:
                self.cache.popitem(last=False)

    def __len__(self):
        with self._lock:
            return len(self.cache)


tile_cache = LRUTileCache(maxsize=128)

# Initialize standalone inference engine (ONNX Runtime with PyTorch eager fallback)
print("Initializing HydroFlow Water Inference Engine...")
engine = WaterInferenceEngine()
def make_error_response(code: str, message: str, status_code: int = 400):
    """Standardized API error response format: {error: {code, message}}"""
    return jsonify({
        "error": {
            "code": code,
            "message": message
        }
    }), status_code


@app.route("/", methods=["GET"])
def index():
    """Serves the main HydroFlow unified web interface."""
    samples = []
    if os.path.exists(SAMPLES_META_PATH):
        try:
            with open(SAMPLES_META_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                samples = data.get("samples", [])
        except Exception as e:
            print(f"Error loading samples metadata: {e}")
            
    return render_template(
        "index.html",
        samples=samples,
        model_name="ResNet-34 SMP U-Net",
        device=str(engine.device).upper(),
        global_iou="81.66%",
        peak_iou="82.10%",
        precision="91.48%",
        recall="88.39%",
        f1_score="89.91%"
    )


@app.route("/docs", methods=["GET"])
def docs():
    """Serves the interactive REST API documentation page."""
    return render_template("docs.html")


@app.route("/health", methods=["GET"])
def health():
    """Health check and model capability endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": {
            "name": "HydroFlow Pretrained SMP U-Net",
            "backbone": BACKBONE,
            "input_channels": IN_CHANNELS,
            "classes": CLASSES,
            "backend": engine.backend,
            "device": str(engine.device),
            "benchmark_global_iou_pct": 81.66,
            "benchmark_peak_val_iou_pct": 82.10,
            "benchmark_precision_pct": 91.48,
            "benchmark_recall_pct": 88.39,
            "benchmark_f1_pct": 89.91,
            "input_resolution": [128, 128]
        },
        "endpoints": {
            "predict": "POST /predict?format=[image|json]",
            "predict_geo": "POST /predict_geo",
            "samples": "GET /samples",
            "health": "GET /health"
        }
    })


@app.route("/samples", methods=["GET"])
def get_samples():
    """Returns metadata for the 3 prepackaged validation test samples."""
    if not os.path.exists(SAMPLES_META_PATH):
        return make_error_response("SAMPLES_NOT_FOUND", "Samples metadata file not found", 404)
        
    with open(SAMPLES_META_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)


@app.route("/predict", methods=["POST"])
def predict():
    """
    Core Task 4 Water Segmentation Endpoint.
    Accepts:
      - Multipart file upload: `file` or `image`
      - OR JSON payload with `sample_id` (e.g., 'sample_1_lake')
      - Query param `format`: 'image' (returns binary PNG mask) or 'json' (returns rich JSON)
      - Query/Form/JSON param `threshold`: float (default 0.5)
    """
    req_format = request.args.get("format", "json").lower()
    
    # Parse threshold
    threshold = request.args.get("threshold", None)
    if threshold is None and request.is_json:
        threshold = request.json.get("threshold", None)
    if threshold is None and request.form:
        threshold = request.form.get("threshold", None)
        
    try:
        threshold = float(threshold) if threshold is not None else THRESHOLD
        threshold = max(0.01, min(0.99, threshold))
    except (ValueError, TypeError):
        threshold = THRESHOLD

    input_data = None
    filename = "uploaded_scene.tif"

    # Check for direct prepackaged sample request
    sample_id = request.args.get("sample", None) or request.args.get("sample_id", None)
    if not sample_id and request.is_json:
        sample_id = request.json.get("sample_id", None) or request.json.get("sample", None)
    if not sample_id and request.form:
        sample_id = request.form.get("sample_id", None) or request.form.get("sample", None)

    if sample_id:
        clean_id = os.path.basename(sample_id).replace(".tif", "")
        sample_path = os.path.join(SAMPLES_DIR, f"{clean_id}.tif")
        if os.path.exists(sample_path):
            input_data = sample_path
            filename = f"{clean_id}.tif"
        else:
            return make_error_response("SAMPLE_NOT_FOUND", f"Sample '{clean_id}' not found in {SAMPLES_DIR}", 404)

    # Check for uploaded multipart file
    if input_data is None:
        file_obj = None
        if "file" in request.files:
            file_obj = request.files["file"]
        elif "image" in request.files:
            file_obj = request.files["image"]

        if file_obj and file_obj.filename != "":
            filename = file_obj.filename
            input_data = file_obj.read()

    # Check for base64 in JSON
    if input_data is None and request.is_json:
        b64_str = request.json.get("image_base64", None)
        if b64_str:
            import base64
            if "," in b64_str:
                b64_str = b64_str.split(",")[1]
            input_data = base64.b64decode(b64_str)
            filename = "base64_scene.png"

    if input_data is None:
        return make_error_response(
            "MISSING_INPUT",
            "No input provided. Upload a file via multipart form-data ('file'), specify a 'sample_id', or provide 'image_base64'.",
            400
        )

    try:
        # Execute inference pipeline
        res = engine.predict(input_data, threshold=threshold)
    except (ValueError, TypeError) as e:
        return make_error_response("INVALID_IMAGE_FORMAT", f"Invalid input image or unsupported format: {str(e)}", 400)
    except Exception as e:
        err_msg = str(e)
        if "cannot identify image" in err_msg.lower() or "not a tiff" in err_msg.lower() or "unidentified" in err_msg.lower():
            return make_error_response("CORRUPTED_FILE", f"Invalid image file format or corrupted file: {err_msg}", 400)
        return make_error_response("INFERENCE_FAILED", f"Inference execution failed: {err_msg}", 500)

    # Handle binary PNG mask stream response (task 4 format=image)
    if req_format == "image":
        png_bytes = engine.to_bytes(res["mask_preview"], format="PNG")
        response = Response(png_bytes, mimetype="image/png")
        response.headers["X-Water-Percentage"] = f"{res['water_percentage']:.2f}"
        response.headers["X-Water-Pixels"] = str(res["water_pixels"])
        response.headers["X-Total-Pixels"] = str(res["total_pixels"])
        response.headers["X-Confidence-Mean"] = f"{res['confidence_mean']:.2f}"
        response.headers["X-Latency-Ms"] = f"{res['latency_ms']:.2f}"
        response.headers["Content-Disposition"] = f'inline; filename="water_mask_{os.path.splitext(filename)[0]}.png"'
        return response

    # Handle rich JSON response (task 4 format=json)
    is_multi = res.get("is_multispectral", True)
    return jsonify({
        "success": True,
        "filename": filename,
        "is_multispectral": is_multi,
        "input_channels": res.get("input_channels", 12),
        "ood_warning": None if is_multi else "Notice: Optical 3-band RGB fallback detected. Model trained on 12 multispectral bands; results are indicative.",
        "water_percentage": res["water_percentage"],
        "water_pixels": res["water_pixels"],
        "total_pixels": res["total_pixels"],
        "confidence_mean": res["confidence_mean"],
        "threshold_used": res["threshold_used"],
        "latency_ms": res["latency_ms"],
        "dimensions": res["dimensions"],
        "device_used": res["device_used"],
        "images": {
            "rgb_preview": engine.to_base64(res["rgb_preview"]),
            "mask_preview": engine.to_base64(res["mask_preview"]),
            "overlay_preview": engine.to_base64(res["overlay_preview"])
        }
    })


@app.route("/predict_geo", methods=["POST"])
def predict_geo():
    """
    Advanced Star-Track Earth Explorer Endpoint.
    Uses singleton connection pooling and LRU tile cache.
    Supports multi-scale footprints and free-form visible viewport analysis:
      - 'small': Single satellite tile (~20 km, 1x1 footprint)
      - 'medium': Expanded regional grid (~50 km, 2x2 footprint)
      - 'large': Broad regional coverage (~100 km, 3x3 footprint)
      - 'viewport': Free-form full visible viewport of the map screen
    """
    data = request.get_json(silent=True) or {}
    try:
        lat = float(data.get("lat", 22.45))
        lon = float(data.get("lon", 31.85))
        zoom = int(data.get("zoom", 13))
        threshold = float(data.get("threshold", THRESHOLD))
        area_mode = str(data.get("area_mode", "small")).lower()
        viewport_bounds = data.get("viewport_bounds", None)
    except (ValueError, TypeError):
        return make_error_response("INVALID_COORDINATES", "Invalid coordinates or zoom format.", 400)

    # Base Web Mercator tile index calculation
    zoom = max(2, min(17, zoom))
    n = 2.0 ** zoom
    lat_rad = math.radians(lat)
    xtile = int((lon + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)

    # Compute base tile bounding box
    lon_tile_min = xtile / n * 360.0 - 180.0
    lon_tile_max = (xtile + 1) / n * 360.0 - 180.0
    lat_rad_max = math.atan(math.sinh(math.pi * (1.0 - 2.0 * ytile / n)))
    lat_rad_min = math.atan(math.sinh(math.pi * (1.0 - 2.0 * (ytile + 1) / n)))
    lat_tile_max = math.degrees(lat_rad_max)
    lat_tile_min = math.degrees(lat_rad_min)
    dlat = max(0.001, lat_tile_max - lat_tile_min)
    dlon = max(0.001, lon_tile_max - lon_tile_min)

    # Determine GPS bounding box and resolution by area_mode
    if area_mode == "viewport" and viewport_bounds and len(viewport_bounds) == 2:
        try:
            lat_min = float(viewport_bounds[0][0])
            lon_min = float(viewport_bounds[0][1])
            lat_max = float(viewport_bounds[1][0])
            lon_max = float(viewport_bounds[1][1])
            img_w, img_h = 512, 384
        except Exception:
            lat_min, lat_max = lat_tile_min, lat_tile_max
            lon_min, lon_max = lon_tile_min, lon_tile_max
            img_w, img_h = 256, 256
    elif area_mode == "large":
        lat_min = max(-85.0, lat - 1.5 * dlat)
        lat_max = min(85.0, lat + 1.5 * dlat)
        lon_min = max(-180.0, lon - 1.5 * dlon)
        lon_max = min(180.0, lon + 1.5 * dlon)
        img_w, img_h = 512, 512
    elif area_mode == "medium":
        lat_min = max(-85.0, lat - 1.0 * dlat)
        lat_max = min(85.0, lat + 1.0 * dlat)
        lon_min = max(-180.0, lon - 1.0 * dlon)
        lon_max = min(180.0, lon + 1.0 * dlon)
        img_w, img_h = 384, 384
    else:
        area_mode = "small"
        lat_min, lat_max = lat_tile_min, lat_tile_max
        lon_min, lon_max = lon_tile_min, lon_tile_max
        img_w, img_h = 256, 256

    bounds = [[lat_min, lon_min], [lat_max, lon_max]]
    cache_key = (round(lat_min, 4), round(lon_min, 4), round(lat_max, 4), round(lon_max, 4), img_w, img_h)
    headers = {"User-Agent": "HydroFlow-WaterSegmentation/2.0"}

    # 1. Check LRU Cache
    raw_tile_img = tile_cache.get(cache_key)
    if raw_tile_img is not None:
        raw_tile_img = raw_tile_img.copy()

    # 2. Fetch via connection-pooled session if not cached
    if raw_tile_img is None:
        export_url = (
            f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export"
            f"?bbox={lon_min},{lat_min},{lon_max},{lat_max}&bboxSR=4326&size={img_w},{img_h}"
            f"&imageSR=4326&format=png&f=image"
        )
        try:
            resp = http_session.get(export_url, headers=headers, timeout=6)
            if resp.status_code == 200:
                raw_tile_img = Image.open(io.BytesIO(resp.content)).convert("RGB")
                tile_cache.put(cache_key, raw_tile_img)
        except Exception as e:
            print(f"ArcGIS export fetch failed: {e}")

    # Fallback for single tile if export failed
    if raw_tile_img is None and area_mode == "small":
        tile_url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{ytile}/{xtile}"
        try:
            resp = http_session.get(tile_url, headers=headers, timeout=4)
            if resp.status_code == 200:
                raw_tile_img = Image.open(io.BytesIO(resp.content)).convert("RGB")
                tile_cache.put(cache_key, raw_tile_img)
        except Exception:
            pass

    # If satellite imagery could not be fetched, return honest 502 error instead of fake synthetic data
    if raw_tile_img is None:
        return make_error_response(
            "UPSTREAM_TILE_ERROR",
            f"Satellite imagery could not be retrieved from provider for coordinates [{lat:.4f}, {lon:.4f}]. Please check network connectivity and retry.",
            502
        )

    # Resize image to multiple of 32 for U-Net architecture
    inf_w = max(128, min(512, (raw_tile_img.width // 32) * 32))
    inf_h = max(128, min(512, (raw_tile_img.height // 32) * 32))
    inference_img = raw_tile_img.resize((inf_w, inf_h), Image.Resampling.BILINEAR)

    # Execute segmentation model
    res = engine.predict(inference_img, threshold=threshold)

    # Create transparent PNG mask for Leaflet ImageOverlay
    bin_mask = res["binary_mask"]
    h, w = bin_mask.shape
    rgba_overlay = np.zeros((h, w, 4), dtype=np.uint8)
    water_px = bin_mask > 0
    # Water data overlay: (0, 212, 229, 180)
    rgba_overlay[water_px, 0] = 0
    rgba_overlay[water_px, 1] = 212
    rgba_overlay[water_px, 2] = 229
    rgba_overlay[water_px, 3] = 180

    transparent_mask_img = Image.fromarray(rgba_overlay, mode="RGBA")
    if transparent_mask_img.size != raw_tile_img.size:
        transparent_mask_img = transparent_mask_img.resize(raw_tile_img.size, Image.Resampling.NEAREST)

    return jsonify({
        "success": True,
        "coordinates": {"lat": lat, "lon": lon, "zoom": zoom},
        "area_mode": area_mode,
        "bounds": bounds,
        "is_multispectral": False,
        "input_channels": 3,
        "ood_warning": "Notice: Map satellite imagery provides optical RGB bands. Multispectral bands B1, B5-B8A, B11-B12 are synthesized from RGB. Results are indicative.",
        "water_percentage": res["water_percentage"],
        "water_pixels": res["water_pixels"],
        "total_pixels": res["total_pixels"],
        "confidence_mean": res["confidence_mean"],
        "latency_ms": res["latency_ms"],
        "overlay_base64": engine.to_base64(transparent_mask_img, format="PNG"),
        "rgb_base64": engine.to_base64(raw_tile_img, format="PNG"),
        "mask_base64": engine.to_base64(res["mask_preview"], format="PNG")
    })


@app.errorhandler(413)
def request_entity_too_large(error):
    return make_error_response("FILE_TOO_LARGE", "Uploaded file is too large. Max limit is 32MB.", 413)


@app.errorhandler(404)
def not_found(error):
    return make_error_response("NOT_FOUND", "Resource not found", 404)


@app.errorhandler(500)
def internal_error(error):
    return make_error_response("INTERNAL_SERVER_ERROR", "Internal server error occurred", 500)


if __name__ == "__main__":
    print(f"Starting HydroFlow Flask Platform on http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=DEBUG)
