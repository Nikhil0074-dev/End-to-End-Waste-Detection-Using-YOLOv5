from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


class ModelTrainingError(RuntimeError):
    """Raised when YOLOv5 training fails or emits no checkpoint."""


def train_model(data_yaml: str | Path, yolov5_dir: str | Path, output_dir: str | Path,
                epochs: int = 10, batch_size: int = 16, image_size: int = 416,
                weights: str = "yolov5s.pt") -> Path:
    repo = Path(yolov5_dir).resolve()
    train_script = repo / "train.py"
    if not train_script.is_file():
        raise ModelTrainingError(f"YOLOv5 train.py not found: {train_script}")
    output = Path(output_dir).resolve()
    run_dir = output / "training"
    command = [sys.executable, str(train_script), "--img", str(image_size), "--batch", str(batch_size),
               "--epochs", str(epochs), "--data", str(Path(data_yaml).resolve()), "--weights", weights,
               "--project", str(run_dir), "--name", "waste", "--exist-ok"]
    try:
        subprocess.run(command, cwd=repo, check=True, timeout=int(os.getenv("TRAIN_TIMEOUT", "86400")))
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise ModelTrainingError(f"YOLOv5 training failed: {exc}") from exc
    checkpoint = run_dir / "waste" / "weights" / "best.pt"
    if not checkpoint.is_file():
        raise ModelTrainingError(f"Training completed without checkpoint: {checkpoint}")
    model_destination = output / "models" / "my_model.pt"
    model_destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(checkpoint, model_destination)
    return model_destination
