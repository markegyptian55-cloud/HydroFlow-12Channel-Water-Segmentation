import sys
import os
import time
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class TestEndpointLatencyAndPayload(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_latency(self):
        t0 = time.perf_counter()
        resp = self.client.get('/health')
        latency = (time.perf_counter() - t0) * 1000
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "healthy")
        print(f"\n[Test Health] Latency: {latency:.2f} ms")

    def test_predict_geo_payload_and_caching(self):
        # Round 1: Fetch and infer
        t0 = time.perf_counter()
        resp1 = self.client.post('/predict_geo', json={
            'lat': 22.45,
            'lon': 31.85,
            'zoom': 12,
            'threshold': 0.5,
            'area_mode': 'small'
        })
        latency1 = (time.perf_counter() - t0) * 1000
        self.assertEqual(resp1.status_code, 200)
        data1 = resp1.get_json()

        self.assertIn('overlay_base64', data1)
        self.assertNotIn('rgb_base64', data1, "Dead payload rgb_base64 was not stripped!")
        self.assertNotIn('mask_base64', data1, "Dead payload mask_base64 was not stripped!")
        self.assertTrue(data1['overlay_base64'].startswith('data:image/png;base64,'))

        payload_kb = len(resp1.data) / 1024.0
        print(f"[Round 1 Cold/Fetch] Total: {latency1:.2f} ms, Server Infer: {data1['latency_ms']:.2f} ms, Payload: {payload_kb:.1f} KB, Water: {data1['water_percentage']:.2f}%")

        # Round 2: Immediate Cache Hit
        t0 = time.perf_counter()
        resp2 = self.client.post('/predict_geo', json={
            'lat': 22.45,
            'lon': 31.85,
            'zoom': 12,
            'threshold': 0.5,
            'area_mode': 'small'
        })
        latency2 = (time.perf_counter() - t0) * 1000
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.get_json()

        self.assertTrue(data2.get('cached'))
        self.assertEqual(resp2.headers.get('X-Cache'), 'HIT')
        print(f"[Round 2 Cache HIT] Total: {latency2:.2f} ms, Server Cache Fetch: {data2['latency_ms']:.2f} ms, X-Cache: HIT")

if __name__ == '__main__':
    unittest.main()
