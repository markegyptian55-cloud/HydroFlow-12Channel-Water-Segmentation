import os
import time
import torch
import numpy as np

try:
    from .config import (
        BACKBONE, IN_CHANNELS, CLASSES,
        WEIGHTS_PATH, BASE_DIR
    )
    from .models.pretrained_smp import build_pretrained_unet
except ImportError:
    from config import (
        BACKBONE, IN_CHANNELS, CLASSES,
        WEIGHTS_PATH, BASE_DIR
    )
    from models.pretrained_smp import build_pretrained_unet


def export_to_onnx(
    weights_path: str = WEIGHTS_PATH,
    output_onnx_path: str = None,
    opset_version: int = 14
) -> str:
    """
    Exports the PyTorch ResNet-34 12-channel U-Net model to ONNX format
    with dynamic batch size, height, and width axes.
    """
    if output_onnx_path is None:
        weights_dir = os.path.dirname(weights_path)
        output_onnx_path = os.path.join(weights_dir, "best_model.onnx")

    print(f"Loading PyTorch weights from: {weights_path}")
    model = build_pretrained_unet(
        encoder_name=BACKBONE,
        encoder_weights="imagenet",
        in_channels=IN_CHANNELS,
        classes=CLASSES
    )

    state_dict = torch.load(weights_path, map_location="cpu")
    if hasattr(model, "model"):
        model.model.load_state_dict(state_dict)
    else:
        model.load_state_dict(state_dict)

    model.eval()
    model.to("cpu")

    # Create dummy input tensor: (batch=1, channels=12, H=128, W=128)
    dummy_input = torch.randn(1, IN_CHANNELS, 128, 128, dtype=torch.float32)

    print(f"Exporting ONNX model to: {output_onnx_path} (opset={opset_version})...")
    t0 = time.perf_counter()

    torch.onnx.export(
        model,
        dummy_input,
        output_onnx_path,
        export_params=True,
        opset_version=opset_version,
        do_constant_folding=True,
        dynamo=False,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={
            "input": {0: "batch_size", 2: "height", 3: "width"},
            "output": {0: "batch_size", 2: "height", 3: "width"}
        }
    )

    export_time = time.perf_counter() - t0
    file_size_mb = os.path.getsize(output_onnx_path) / (1024 * 1024)
    print(f"Successfully exported ONNX model in {export_time:.2f}s ({file_size_mb:.2f} MB)")

    # Validate with onnx and onnxruntime
    import onnx
    import onnxruntime as ort

    print("Verifying ONNX graph validity...")
    onnx_model = onnx.load(output_onnx_path)
    onnx.checker.check_model(onnx_model)
    print("ONNX graph validation passed.")

    print("Testing ONNX Runtime session execution...")
    opts = ort.SessionOptions()
    opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    session = ort.InferenceSession(output_onnx_path, sess_options=opts, providers=["CPUExecutionProvider"])

    test_input = np.random.randn(1, 12, 128, 128).astype(np.float32)
    ort_outputs = session.run(None, {"input": test_input})
    print(f"ONNX Runtime inference test passed. Output shape: {ort_outputs[0].shape}")

    # Cross-check numerical equivalence with PyTorch
    with torch.no_grad():
        torch_out = model(torch.from_numpy(test_input)).numpy()
    max_diff = np.max(np.abs(torch_out - ort_outputs[0]))
    print(f"Max absolute divergence between PyTorch and ONNX: {max_diff:.6e}")
    assert max_diff < 1e-4, f"Numerical discrepancy too large: {max_diff}"
    print("Numerical parity confirmed (< 1e-4).")

    return output_onnx_path


if __name__ == "__main__":
    export_to_onnx()
