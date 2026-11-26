from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(10 * 1024 * 1024)))
    MODEL_PATH = Path(os.getenv("MODEL_PATH", str(ROOT / "model" / "my_model.pt")))
    YOLOV5_DIR = Path(os.getenv("YOLOV5_DIR", str(ROOT / "yolov5")))
    IMAGE_SIZE = int(os.getenv("IMAGE_SIZE", "416"))
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
    INFERENCE_DEVICE = os.getenv("INFERENCE_DEVICE", "")
    ALLOWED_ORIGINS = [x.strip() for x in os.getenv("ALLOWED_ORIGINS", "").split(",") if x.strip()]
    ARTIFACTS_DIR = Path(os.getenv("ARTIFACTS_DIR", str(ROOT / "artifacts")))
    DATASET_DIR = Path(os.getenv("DATASET_DIR", str(ROOT / "artifacts" / "datasets" / "waste")))
    DATA_YAML = Path(os.getenv("DATA_YAML", str(ROOT / "data.yaml")))
    TRAIN_EPOCHS = int(os.getenv("TRAIN_EPOCHS", "10"))
    TRAIN_BATCH_SIZE = int(os.getenv("TRAIN_BATCH_SIZE", "16"))
    TRAIN_WEIGHTS = os.getenv("TRAIN_WEIGHTS", "yolov5s.pt")
