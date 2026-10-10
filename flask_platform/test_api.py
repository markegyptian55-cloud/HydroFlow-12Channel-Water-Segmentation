"""
Automated Test Suite for HydroFlow Flask Platform REST API.
Verifies all core endpoints, dual response formats (image & json),
and prediction accuracy across the 3 prepackaged validation scenes.
"""
import io
import os
import json
import unittest
from PIL import Image
import numpy as np
import tifffile as tiff

try:
    from app import app
    from config import SAMPLES_DIR
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from app import app
    from config import SAMPLES_DIR


class TestHydroFlowAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.samples = {
            "sample_1_lake": os.path.join(SAMPLES_DIR, "sample_1_lake.tif"),
            "sample_2_river": os.path.join(SAMPLES_DIR, "sample_2_river.tif"),
            "sample_3_stream": os.path.join(SAMPLES_DIR, "sample_3_stream.tif"),
        }
        for name, path in cls.samples.items():
            if not os.path.exists(path):
                raise FileNotFoundError(f"Missing test sample: {path}")

    def test_01_health_endpoint(self):
        """Test GET /health returns 200 and model metadata."""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["model"]["backbone"], "resnet34")
        self.assertEqual(data["model"]["input_channels"], 12)
        self.assertEqual(data["model"]["benchmark_global_iou_pct"], 81.66)

    def test_02_samples_endpoint(self):
        """Test GET /samples returns 200 and lists all 3 validation scenes."""
        resp = self.client.get("/samples")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("samples", data)
        self.assertEqual(len(data["samples"]), 3)
        sample_ids = [s["id"] for s in data["samples"]]
        self.assertIn("sample_1_lake", sample_ids)
        self.assertIn("sample_2_river", sample_ids)
        self.assertIn("sample_3_stream", sample_ids)

    def test_03_predict_multipart_json_lake(self):
        """Test POST /predict?format=json on Sample 1 (Lake, High Water)."""
        with open(self.samples["sample_1_lake"], "rb") as f:
            resp = self.client.post(
                "/predict?format=json",
                data={"file": (f, "sample_1_lake.tif")},
                content_type="multipart/form-data"
            )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertGreater(data["water_percentage"], 50.0)
        self.assertIn("images", data)
        self.assertTrue(data["images"]["mask_preview"].startswith("data:image/png;base64,"))
        self.assertTrue(data["images"]["rgb_preview"].startswith("data:image/png;base64,"))
        self.assertTrue(data["images"]["overlay_preview"].startswith("data:image/png;base64,"))

    def test_04_predict_multipart_json_river(self):
        """Test POST /predict?format=json on Sample 2 (River, Moderate Water)."""
        with open(self.samples["sample_2_river"], "rb") as f:
            resp = self.client.post(
                "/predict?format=json",
                data={"file": (f, "sample_2_river.tif")},
                content_type="multipart/form-data"
            )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertGreater(data["water_percentage"], 15.0)
        self.assertLess(data["water_percentage"], 50.0)

    def test_05_predict_multipart_json_stream(self):
        """Test POST /predict?format=json on Sample 3 (Stream, Low Water)."""
        with open(self.samples["sample_3_stream"], "rb") as f:
            resp = self.client.post(
                "/predict?format=json",
                data={"file": (f, "sample_3_stream.tif")},
                content_type="multipart/form-data"
            )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertGreater(data["water_percentage"], 1.0)
        self.assertLess(data["water_percentage"], 15.0)

    def test_06_predict_multipart_image_stream(self):
        """Test POST /predict?format=image returns pure binary PNG mask stream."""
        with open(self.samples["sample_1_lake"], "rb") as f:
            resp = self.client.post(
                "/predict?format=image",
                data={"file": (f, "sample_1_lake.tif")},
                content_type="multipart/form-data"
            )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, "image/png")
        self.assertIn("X-Water-Percentage", resp.headers)
        self.assertIn("X-Water-Pixels", resp.headers)
        
        # Verify binary stream is readable by PIL
        img = Image.open(io.BytesIO(resp.data))
        self.assertEqual(img.size, (128, 128))

    def test_07_predict_by_sample_id_param(self):
        """Test POST /predict using direct sample_id parameter."""
        resp = self.client.post(
            "/predict?format=json",
            json={"sample_id": "sample_2_river"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertAlmostEqual(data["water_percentage"], 34.35, delta=2.0)

    def test_08_predict_geo_endpoint(self):
        """Test POST /predict_geo with coordinates for Lake Nasser, Egypt."""
        resp = self.client.post(
            "/predict_geo",
            json={"lat": 23.97, "lon": 32.88, "zoom": 13, "threshold": 0.5}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertIn("bounds", data)
        self.assertIn("overlay_base64", data)
        self.assertEqual(len(data["bounds"]), 2)

    def test_09_error_handling_empty_payload(self):
        """Test POST /predict with no payload returns 400 Bad Request."""
        resp = self.client.post("/predict")
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertIn("error", data)

    def test_10_error_handling_invalid_sample(self):
        """Test POST /predict with non-existent sample returns 404."""
        resp = self.client.post("/predict?sample=sample_999_nonexistent")
        self.assertEqual(resp.status_code, 404)

    def test_11_predict_optical_png_upload(self):
        """Test POST /predict with standard 3-channel optical PNG file."""
        # Create synthetic optical RGB image
        img = Image.new("RGB", (128, 128), color=(120, 150, 90))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        resp = self.client.post(
            "/predict?format=json",
            data={"file": (buf, "optical_scene.png")},
            content_type="multipart/form-data"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["dimensions"]["width"], 128)
        self.assertEqual(data["dimensions"]["height"], 128)
        self.assertIn("rgb_preview", data["images"])

    def test_12_predict_channel_first_geotiff(self):
        """Test POST /predict with channel-first (12, H, W) and (3, H, W) GeoTIFF."""
        # 12-channel channel-first (standard GDAL/Rasterio GeoTIFF output)
        arr_12ch = np.random.uniform(50, 1500, (12, 64, 64)).astype(np.float32)
        buf12 = io.BytesIO()
        tiff.imwrite(buf12, arr_12ch)
        buf12.seek(0)

        resp = self.client.post(
            "/predict?format=json",
            data={"file": (buf12, "ch_first_12.tif")},
            content_type="multipart/form-data"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])

        # 3-channel channel-first
        arr_3ch = np.random.uniform(50, 1500, (3, 64, 64)).astype(np.float32)
        buf3 = io.BytesIO()
        tiff.imwrite(buf3, arr_3ch)
        buf3.seek(0)

        resp3 = self.client.post(
            "/predict?format=json",
            data={"file": (buf3, "ch_first_3.tif")},
            content_type="multipart/form-data"
        )
        self.assertEqual(resp3.status_code, 200)
        self.assertTrue(resp3.get_json()["success"])

    def test_13_predict_6band_ablation_geotiff(self):
        """Test POST /predict with 6-band Sentinel-2 ablation subset."""
        arr_6ch = np.random.uniform(100, 2000, (6, 64, 64)).astype(np.float32)
        buf6 = io.BytesIO()
        tiff.imwrite(buf6, arr_6ch)
        buf6.seek(0)

        resp = self.client.post(
            "/predict?format=json",
            data={"file": (buf6, "ablation_6ch.tif")},
            content_type="multipart/form-data"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])

    def test_14_predict_grayscale_1band_geotiff(self):
        """Test POST /predict with 1-channel grayscale GeoTIFF."""
        arr_1ch = np.random.uniform(100, 1000, (1, 64, 64)).astype(np.float32)
        buf1 = io.BytesIO()
        tiff.imwrite(buf1, arr_1ch)
        buf1.seek(0)

        resp = self.client.post(
            "/predict?format=json",
            data={"file": (buf1, "grayscale_1ch.tif")},
            content_type="multipart/form-data"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])

    def test_15_predict_normalized_float_rgb(self):
        """Test that float [0.0, 1.0] RGB input is scaled properly and does not saturate to 100% water."""
        # Bright gray/white scene in float [0, 1]
        arr_float = np.ones((64, 64, 3), dtype=np.float32) * 0.8
        buf = io.BytesIO()
        tiff.imwrite(buf, arr_float)
        buf.seek(0)

        resp = self.client.post(
            "/predict?format=json",
            data={"file": (buf, "float_white.tif")},
            content_type="multipart/form-data"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        # White/bright terrain must NOT be classified as 100% water
        self.assertLess(data["water_percentage"], 30.0)

    def test_16_predict_threshold_effect(self):
        """Test that varying the sigmoid threshold calibrates decision boundary."""
        with open(self.samples["sample_2_river"], "rb") as f:
            file_bytes = f.read()

        resp_low = self.client.post(
            "/predict?format=json&threshold=0.15",
            data={"file": (io.BytesIO(file_bytes), "sample_2_river.tif")},
            content_type="multipart/form-data"
        )
        resp_high = self.client.post(
            "/predict?format=json&threshold=0.85",
            data={"file": (io.BytesIO(file_bytes), "sample_2_river.tif")},
            content_type="multipart/form-data"
        )
        self.assertEqual(resp_low.status_code, 200)
        self.assertEqual(resp_high.status_code, 200)

        water_low = resp_low.get_json()["water_pixels"]
        water_high = resp_high.get_json()["water_pixels"]
        self.assertGreaterEqual(water_low, water_high)

    def test_17_error_handling_corrupted_file(self):
        """Test POST /predict with corrupted/non-image payload returns 400 Bad Request."""
        corrupt_buf = io.BytesIO(b"This is not a valid TIFF or PNG image file.")
        resp = self.client.post(
            "/predict?format=json",
            data={"file": (corrupt_buf, "corrupted.dat")},
            content_type="multipart/form-data"
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertIn("error", data)

    def test_18_docs_and_index_pages(self):
        """Test GET / and GET /docs return HTTP 200 with complete HTML pages."""
        resp_index = self.client.get("/")
        self.assertEqual(resp_index.status_code, 200)
        self.assertIn(b"HydroFlow", resp_index.data)

        resp_docs = self.client.get("/docs")
        self.assertEqual(resp_docs.status_code, 200)
        self.assertIn(b"HydroFlow Water Intelligence API Specification", resp_docs.data)

    def test_19_strip_image_shapes(self):
        """Test that narrow/strip GeoTIFFs (1x32 and 12x1x32) preserve their dimensions without swapping."""
        # Channel-last strip: (1, 32, 12)
        strip_last = np.random.uniform(50, 1000, (1, 32, 12)).astype(np.float32)
        buf1 = io.BytesIO()
        tiff.imwrite(buf1, strip_last)
        buf1.seek(0)
        resp1 = self.client.post(
            "/predict?format=json",
            data={"file": (buf1, "strip_last.tif")},
            content_type="multipart/form-data"
        )
        self.assertEqual(resp1.status_code, 200)
        data1 = resp1.get_json()
        self.assertEqual(data1["dimensions"]["height"], 1)
        self.assertEqual(data1["dimensions"]["width"], 32)

        # Channel-first strip: (12, 1, 32)
        strip_first = np.random.uniform(50, 1000, (12, 1, 32)).astype(np.float32)
        buf2 = io.BytesIO()
        tiff.imwrite(buf2, strip_first)
        buf2.seek(0)
        resp2 = self.client.post(
            "/predict?format=json",
            data={"file": (buf2, "strip_first.tif")},
            content_type="multipart/form-data"
        )
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.get_json()
        self.assertEqual(data2["dimensions"]["height"], 1)
        self.assertEqual(data2["dimensions"]["width"], 32)

    def test_20_concurrent_tile_cache_access(self):
        """Test that LRUTileCache is thread-safe under concurrent read/write access."""
        import threading
        from app import LRUTileCache
        cache = LRUTileCache(maxsize=16)
        dummy_img = Image.new("RGB", (64, 64), color="blue")
        errors = []

        def worker(w_id):
            try:
                for i in range(100):
                    key = (w_id, i % 10)
                    cache.put(key, dummy_img)
                    val = cache.get(key)
                    if val is None:
                        # May have been evicted, but shouldn't raise exceptions
                        pass
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(t,)) for t in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Thread-safety errors encountered: {errors}")
        self.assertLessEqual(len(cache), 16)


if __name__ == "__main__":
    unittest.main()
