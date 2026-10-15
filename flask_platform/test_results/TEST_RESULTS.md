# API Test Results (Task 4)

Measured inference results on the 3 prepackaged validation scenes via `/predict` REST endpoint:

| Sample | HTTP | Water % | Water Pixels | Mean Confidence | Latency | Mask |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `sample_1_lake` | 200 | 78.31% | 12,831 / 16,384 | 97.67% | 30.81 ms | [`sample_1_lake_mask.png`](sample_1_lake_mask.png) |
| `sample_2_river` | 200 | 34.35% | 5,628 / 16,384 | 98.59% | 27.60 ms | [`sample_2_river_mask.png`](sample_2_river_mask.png) |
| `sample_3_stream` | 200 | 9.11% | 1,493 / 16,384 | 95.61% | 27.63 ms | [`sample_3_stream_mask.png`](sample_3_stream_mask.png) |
