from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

from flask import current_app


class InferenceError(RuntimeError):
    """Raised when model inference cannot be completed."""


def detect(image_bytes: bytes) -> bytes:
    model_path = Path(current_app.config["MODEL_PATH"])
    yolo_dir = Path(current_app.config["YOLOV5_DIR"])
    script = yolo_dir / "detect.py"
    if not model_path.is_file():
        raise FileNotFoundError(f"Model checkpoint not found: {model_path}")
    if not script.is_file():
        raise FileNotFoundError(f"YOLOv5 detect.py not found: {script}")

    with tempfile.TemporaryDirectory(prefix="waste-detect-") as temp:
        temp_path = Path(temp)
        source = temp_path / "input.png"
        output = temp_path / "output"
        source.write_bytes(image_bytes)
        command = [
            os.getenv("PYTHON", "python"), str(script), "--weights", str(model_path),
            "--source", str(source), "--imgsz", str(current_app.config["IMAGE_SIZE"]),
            "--conf-thres", str(current_app.config["CONFIDENCE_THRESHOLD"]),
            "--project", str(output), "--name", "prediction", "--exist-ok",
        ]
        device = current_app.config.get("INFERENCE_DEVICE")
        if device:
            command.extend(["--device", str(device)])
        try:
            subprocess.run(command, cwd=yolo_dir, check=True, capture_output=True, text=True, timeout=120)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            detail = getattr(exc, "stderr", "")
            raise InferenceError(f"YOLOv5 inference failed: {str(detail)[-1000:]}") from exc
        result = output / "prediction" / source.name
        if not result.is_file():
            raise InferenceError("YOLOv5 completed without producing an annotated image.")
        return result.read_bytes()
