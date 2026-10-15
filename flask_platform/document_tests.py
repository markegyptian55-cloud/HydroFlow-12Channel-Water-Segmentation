"""
Document API Test Results (Task 4)
Executes REST API test runs on the 3 primary validation scenes,
saves binary output masks, and writes a verified results table to TEST_RESULTS.md.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app
from config import SAMPLES_DIR


def main():
    test_client = app.test_client()
    results_dir = os.path.join(BASE_DIR, "test_results")
    os.makedirs(results_dir, exist_ok=True)

    samples = [
        ("sample_1_lake", "sample_1_lake.tif"),
        ("sample_2_river", "sample_2_river.tif"),
        ("sample_3_stream", "sample_3_stream.tif"),
    ]

    records = []

    for sample_id, filename in samples:
        file_path = os.path.join(SAMPLES_DIR, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Missing sample file: {file_path}")

        # 1. POST /predict?format=json
        with open(file_path, "rb") as f:
            resp_json = test_client.post(
                "/predict?format=json",
                data={"file": (f, filename)},
                content_type="multipart/form-data"
            )

        status_code = resp_json.status_code
        json_data = resp_json.get_json() or {}

        water_pct = json_data.get("water_percentage", 0.0)
        water_px = json_data.get("water_pixels", 0)
        total_px = json_data.get("total_pixels", 16384)
        conf_mean = json_data.get("confidence_mean", 0.0)
        latency = json_data.get("latency_ms", 0.0)

        # 2. POST /predict?format=image
        with open(file_path, "rb") as f:
            resp_img = test_client.post(
                "/predict?format=image",
                data={"file": (f, filename)},
                content_type="multipart/form-data"
            )

        mask_filename = f"{sample_id}_mask.png"
        mask_path = os.path.join(results_dir, mask_filename)
        with open(mask_path, "wb") as mf:
            mf.write(resp_img.data)

        records.append({
            "sample": sample_id,
            "http": status_code,
            "water_pct": water_pct,
            "water_pixels": f"{water_px:,} / {total_px:,}",
            "conf_mean": f"{conf_mean:.2f}%",
            "latency": f"{latency:.2f} ms",
            "mask": mask_filename
        })

    # Build Markdown Table
    table_lines = [
        "| Sample | HTTP | Water % | Water Pixels | Mean Confidence | Latency | Mask |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :--- |"
    ]

    for r in records:
        line = f"| `{r['sample']}` | {r['http']} | {r['water_pct']:.2f}% | {r['water_pixels']} | {r['conf_mean']} | {r['latency']} | [`{r['mask']}`]({r['mask']}) |"
        table_lines.append(line)

    markdown_content = "\n".join(table_lines) + "\n"

    # Save to TEST_RESULTS.md
    test_results_path = os.path.join(results_dir, "TEST_RESULTS.md")
    with open(test_results_path, "w", encoding="utf-8") as rf:
        rf.write("# API Test Results (Task 4)\n\n")
        rf.write("Measured inference results on the 3 prepackaged validation scenes via `/predict` REST endpoint:\n\n")
        rf.write(markdown_content)

    print("\n" + markdown_content)
    print(f"Results successfully written to: {test_results_path}")


if __name__ == "__main__":
    main()
