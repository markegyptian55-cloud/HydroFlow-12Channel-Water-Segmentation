---
title: HydroFlow Water Segmentation Platform
emoji: 🌊
colorFrom: blue
colorTo: indigo
sdk: static
app_port: 7860
pinned: false
license: mit
full_width: true
---

# 🌊 HydroFlow: Satellite Water Intelligence Platform

[![Live Space](https://img.shields.io/badge/Hugging%20Face-Live%20Space-FFD21E.svg?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/spaces/egyx/hydroflow-water-segmentation)
[![Direct Fullscreen App](https://img.shields.io/badge/Direct%20App-Fullscreen%20Web-00bcd4.svg?style=for-the-badge&logo=firefox&logoColor=white)](https://egyx-hydroflow-water-segmentation.static.hf.space)
[![Research Dashboard](https://img.shields.io/badge/Research%20Dashboard-GitHub%20Pages-2ea44f.svg?style=for-the-badge&logo=github&logoColor=white)](https://markegyptian55-cloud.github.io/HydroFlow-12Channel-Water-Segmentation/)
[![Model Hub](https://img.shields.io/badge/Hugging%20Face-Model%20Hub-orange.svg?style=for-the-badge&logo=huggingface&logoColor=white)](https://huggingface.co/egyx/hydroflow-water-segmentation)
[![Kaggle Collection](https://img.shields.io/badge/Kaggle-Research%20Collection%20(6%20Notebooks)-20BEFF.svg?style=for-the-badge&logo=kaggle)](https://www.kaggle.com/work/collections/19309568)

> 🚀 **Official Live Access Links**:
> - 🌐 **Direct Fullscreen Web Application (No HF wrapper borders / 100% Fullscreen)**:  
>   [**https://egyx-hydroflow-water-segmentation.static.hf.space**](https://egyx-hydroflow-water-segmentation.static.hf.space)
> - 🤗 **Hugging Face Spaces Portal**:  
>   [**https://huggingface.co/spaces/egyx/hydroflow-water-segmentation**](https://huggingface.co/spaces/egyx/hydroflow-water-segmentation)
> - 📊 **Interactive Research Dashboard (GitHub Pages)**:  
>   [**https://markegyptian55-cloud.github.io/HydroFlow-12Channel-Water-Segmentation/**](https://markegyptian55-cloud.github.io/HydroFlow-12Channel-Water-Segmentation/)
> - 📦 **Model Checkpoints on HF Model Hub**:  
>   [**https://huggingface.co/egyx/hydroflow-water-segmentation**](https://huggingface.co/egyx/hydroflow-water-segmentation)
> - 📓 **Official Kaggle Research Collection (6 Notebooks)**:  
>   [**https://www.kaggle.com/work/collections/19309568**](https://www.kaggle.com/work/collections/19309568)

Production-grade, standalone web application and REST API for **Autonomous Multispectral Water Segmentation** on Sentinel-2 satellite imagery.

Powered by the champion **12-Channel Pretrained ResNet-34 U-Net** (**81.66% Global IoU**, **91.48% Precision**, **89.91% F1-Score**), accelerated with **ONNX Runtime** and deployed on **Hugging Face Spaces**.

---

## Key Features

1. **Standalone & Self-Contained**:
   - Packaged with the champion ResNet-34 model weights (`weights/best_model.pth` and `weights/best_model.onnx`).
   - Self-contained inference engine and model definition (`models/pretrained_smp.py`).
2. **Dual-Mode REST API (`task 4.pdf`)**:
   - `POST /predict?format=image`: Streams raw binary PNG mask with telemetry in HTTP headers (`X-Water-Percentage`, `X-Latency-Ms`).
   - `POST /predict?format=json`: Returns JSON payload with water percentage, pixel counts, confidence, latency, and base64 previews.
3. **Prepackaged Validation Benchmark**:
   - Bundled with 3 verified validation scenes from the test split:
     - **Sample 1 (Lake)**: Expansive reservoir (`76.90% GT | 93.88% IoU`).
     - **Sample 2 (River)**: Meandering river and shoreline (`35.28% GT | 96.15% IoU`).
     - **Sample 3 (Stream)**: Thin tributaries and marshland (`8.02% GT | 87.38% IoU`).
4. **Interactive Earth Satellite Explorer**:
   - High-resolution dynamic satellite basemap powered by Leaflet.js and Esri World Imagery.
   - Click anywhere on Earth (e.g. Lake Nasser, Nile River, Lake Mead) to place a target beacon, query live imagery, run the segmentation model, and overlay predicted water contours directly on the globe.
5. **Scientific Instrument UI & Token-Driven Design**:
   - Pure token-driven CSS architecture with zero CDN dependencies (zero Tailwind CDN, zero FontAwesome CDN).
   - Light and dark themes adhering strictly to WCAG 2.2 AA contrast standards (>= 14:1 contrast).
   - Water data color (`--water-data`) reserved strictly for water reconstructions; interactive UI controls use deep blue-teal (`--accent-primary`).
   - Before/after interactive split comparison slider with touch protection.
   - Comprehensive telemetry, honest Out-of-Distribution (OOD) indicators, and direct PNG/JSON export.
6. **ONNX Runtime & Connection Pooling Acceleration**:
   - Model latency reduced to sub-25ms using multi-threaded ONNX Runtime graph execution.
   - In-memory LRU tile caching (128 slots) and `requests.Session` connection pooling for instant satellite tile retrieval.

---

## Directory Layout

```
flask_platform/
├── Dockerfile                     # Production container spec for Hugging Face Spaces
├── deploy_hf.py                   # Automated Hugging Face Space deployment pipeline
├── export_onnx.py                 # PyTorch-to-ONNX dynamic axis export script
├── app.py                         # Main Flask application with routes (/predict, /predict_geo, /samples, /health)
├── config.py                      # Exact 12-band calibration bounds, model constants, default ports
├── inference.py                   # Production ONNX Runtime & PyTorch inference engine (ResNet-34 12-channel)
├── test_api.py                    # Automated test suite testing all endpoints and samples
├── run.py                         # Single-command launcher (`python run.py`)
├── requirements.txt               # Standalone production dependencies
├── models/
│   ├── __init__.py
│   └── pretrained_smp.py          # Standalone SMP U-Net model definition
├── weights/
│   ├── best_model.pth             # Extracted ResNet-34 12ch state dict (~98 MB)
│   └── best_model.onnx            # Dynamic-axes ONNX Runtime model (~93 MB)
├── static/
│   ├── css/
│   │   └── style.css              # Custom styling, glassmorphism cards, comparison slider
│   ├── js/
│   │   ├── main.js                # Drag & drop upload, sample runner, result renderer
│   │   └── map_explorer.js        # Leaflet interactive satellite map
│   └── samples/
│       ├── sample_1_lake.tif      # High water coverage scene (12 bands)
│       ├── sample_2_river.tif     # River scene (12 bands)
│       ├── sample_3_stream.tif    # Narrow stream scene (12 bands)
│       └── samples_meta.json      # Ground truth metrics and sample descriptions
├── templates/
│   ├── index.html                 # Main unified application UI
│   └── docs.html                  # Interactive API documentation page
└── README.md                      # Hugging Face Space card and technical documentation
```

---

## Quickstart Guide

### 1. Installation
Install the dependencies:
```bash
pip install -r requirements.txt
```

### 2. Launch the Platform
Start the local server:
```bash
python run.py
```
Open your browser at:
- **Web Interface**: [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **API Documentation**: [http://127.0.0.1:5000/docs](http://127.0.0.1:5000/docs)
- **Health Check**: [http://127.0.0.1:5000/health](http://127.0.0.1:5000/health)

### 3. Run Automated Tests
Execute the test suite verifying all endpoints, response formats, and validation samples:
```bash
python test_api.py
```

---

## REST API Reference

### 1. `POST /predict`
Segment water from an uploaded raster or preset sample.

#### Option A: Direct Binary PNG Mask Stream (`format=image`)
```bash
curl -X POST "http://127.0.0.1:5000/predict?format=image" \
     -F "file=@static/samples/sample_1_lake.tif" \
     --output water_mask.png
```

Response:
- **Content-Type**: `image/png`
- **Headers**:
  - `X-Water-Percentage`: `78.31`
  - `X-Water-Pixels`: `12830`
  - `X-Confidence-Mean`: `98.7`
  - `X-Latency-Ms`: `22.45`

#### Option B: Analytical JSON Payload (`format=json`)
```bash
curl -X POST "http://127.0.0.1:5000/predict?format=json" \
     -F "file=@static/samples/sample_1_lake.tif" \
     -F "threshold=0.50"
```

Response JSON:
```json
{
  "success": true,
  "filename": "sample_1_lake.tif",
  "water_percentage": 78.31,
  "water_pixels": 12830,
  "total_pixels": 16384,
  "confidence_mean": 98.7,
  "threshold_used": 0.5,
  "latency_ms": 22.45,
  "dimensions": { "width": 128, "height": 128 },
  "images": {
    "rgb_preview": "data:image/png;base64,...",
    "mask_preview": "data:image/png;base64,...",
    "overlay_preview": "data:image/png;base64,..."
  }
}
```

#### Option C: 1-Click Inference on Bundled Presets
```bash
curl -X POST "http://127.0.0.1:5000/predict?format=json" \
     -H "Content-Type: application/json" \
     -d '{"sample_id": "sample_1_lake"}'
```

---

## 2. `POST /predict_geo`
Fetch satellite imagery for any global coordinate and return a georeferenced water mask overlay.

```bash
curl -X POST "http://127.0.0.1:5000/predict_geo" \
     -H "Content-Type: application/json" \
     -d '{"lat": 22.45, "lon": 31.85, "zoom": 12, "threshold": 0.5}'
```

Response JSON:
```json
{
  "success": true,
  "coordinates": { "lat": 22.45, "lon": 31.85, "zoom": 12 },
  "bounds": [[22.431, 31.816], [22.512, 31.904]],
  "water_percentage": 65.4,
  "water_pixels": 10715,
  "total_pixels": 16384,
  "latency_ms": 58.2,
  "overlay_base64": "data:image/png;base64,..."
}
```

---

## 3. `GET /samples`
Returns metadata and paths for the 3 prepackaged validation scenes.

```bash
curl http://127.0.0.1:5000/samples
```

---

## 4. `GET /health`
Returns service status, model specifications, and benchmark metrics.

```bash
curl http://127.0.0.1:5000/health
```
