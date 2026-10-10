# HydroFlow Deployment Architecture & Hosting Strategy (DEPLOY.md)

**Target**: Provide a real, working, cost-effective (free or near-free) cloud backend for HydroFlow's PyTorch & ONNX Runtime segmentation inference, with clear separation between frontend client and model inference service.

---

## 1. Cloud Provider Comparative Evaluation

We evaluated five modern deployment pathways against the memory footprint of HydroFlow (`PyTorch + ResNet-34 + ONNX Runtime` = ~800 MB baseline RAM requirement during cold start):

| Provider & Tier | Cost | Hardware Specs | Feasibility for HydroFlow | Recommendation |
| :--- | :---: | :---: | :--- | :---: |
| **Hugging Face Space (`sdk: gradio`)** | **$0 / mo (Free)** | **2 vCPU, 16 GB RAM** | **100% Feasible**. Gradio Space runs a full Python 3.10 environment. We can mount FastAPI/Flask directly on port 7860. Massive 16 GB RAM prevents any OOM risks. | ⭐ **Top Recommendation (Primary Cloud Engine)** |
| **Hugging Face Space (`sdk: docker`)** | $9 / mo (PRO) | 2 vCPU, 16 GB RAM | Requires paid PRO account since recent HF policy change (HTTP 402 on new Docker spaces for free users). | Fallback for organizations with PRO |
| **Render.com (Free Web Service)** | $0 / mo | 0.5 CPU, 512 MB RAM | **Fails OOM**. PyTorch model loading immediately triggers Linux OOM killer (Signal 9) exceeding the 512 MB hard ceiling. | Not viable for deep learning |
| **Railway.app (Hobby)** | $5 / mo credit | 1–8 GB RAM | Highly performant, but free trial requires credit card validation and expires after exhaustion. | Secondary option |
| **Fly.io (Hobby/Free)** | $0–$3 / mo | 256–1024 MB RAM | 256 MB free machines fail OOM. 1024 MB requires paid configuration. | Secondary option |

---

## 2. Recommended Production Architecture

### Decoupled Frontend & Backend Architecture
To achieve 100% uptime and allow users to run HydroFlow anywhere (locally, on GitHub Pages, on Hugging Face, or on private clouds), the frontend reads the API base URL from a single global configuration variable:

```javascript
// Centralized API Configuration (static/js/config.js)
window.HYDROFLOW_CONFIG = {
    // Priority:
    // 1. Explicit window override
    // 2. Query parameter: ?api=https://my-backend.hf.space
    // 3. Localhost if running locally
    // 4. Default production cloud backend
    apiBaseUrl: (() => {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('api')) return urlParams.get('api');
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return window.location.origin;
        }
        // Active cloud inference endpoint
        return 'https://egyx-hydroflow-water-segmentation.hf.space';
    })(),
    timeoutMs: 30000,
    maxUploadSizeBytes: 32 * 1024 * 1024 // 32 MB
};
```

### Hugging Face Space Free Python Setup (`sdk: gradio`)
By setting `sdk: gradio` in `README.md` and mounting FastAPI in `app.py`:
1. Hugging Face provisions a dedicated container on port `7860` with **16 GB RAM**.
2. Both `/predict` and `/predict_geo` execute real multi-threaded ONNX Runtime models with zero simulated fallbacks.
3. CORS headers (`Access-Control-Allow-Origin: *`) allow any web client to query the model cleanly.

---

## 3. Step-by-Step Deployment Guide

### Option 1: Single-Command Hugging Face Cloud Deployment
```bash
python flask_platform/deploy_hf.py --mode gradio
```

### Option 2: Local Production Server (Gunicorn)
```bash
cd flask_platform
pip install -r requirements.txt
python run.py
# Server listening at http://127.0.0.1:5000
```

### Option 3: Production Docker Container
```bash
docker build -t hydroflow-platform flask_platform/
docker run -p 7860:7860 hydroflow-platform
```
