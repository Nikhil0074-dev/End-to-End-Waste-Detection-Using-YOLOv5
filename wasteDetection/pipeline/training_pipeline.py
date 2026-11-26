from __future__ import annotations

from config import Settings
from wasteDetection.components.data_ingestion import ingest_dataset
from wasteDetection.components.data_validation import validate_dataset
from wasteDetection.components.model_trainer import train_model


def run_training_pipeline() -> str:
    dataset = ingest_dataset(destination=Settings.DATASET_DIR)
    validate_dataset(dataset, Settings.DATA_YAML)
    checkpoint = train_model(
        data_yaml=Settings.DATA_YAML,
        yolov5_dir=Settings.YOLOV5_DIR,
        output_dir=Settings.ARTIFACTS_DIR,
        epochs=Settings.TRAIN_EPOCHS,
        batch_size=Settings.TRAIN_BATCH_SIZE,
        image_size=Settings.IMAGE_SIZE,
        weights=Settings.TRAIN_WEIGHTS,
    )
    Settings.MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    if checkpoint.resolve() != Settings.MODEL_PATH.resolve():
        from shutil import copy2
        copy2(checkpoint, Settings.MODEL_PATH)
    return str(Settings.MODEL_PATH)
