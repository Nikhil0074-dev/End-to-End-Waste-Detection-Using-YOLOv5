from __future__ import annotations

from pathlib import Path

import yaml


class DatasetValidationError(ValueError):
    """Raised when dataset paths or class configuration are invalid."""


def validate_dataset(dataset_dir: str | Path, data_yaml: str | Path) -> dict:
    root = Path(dataset_dir).resolve()
    config_path = Path(data_yaml).resolve()
    if not root.is_dir():
        raise DatasetValidationError(f"Dataset directory does not exist: {root}")
    if not config_path.is_file():
        raise DatasetValidationError(f"Dataset YAML does not exist: {config_path}")
    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise DatasetValidationError(f"Unable to read dataset YAML: {exc}") from exc
    if not isinstance(config, dict):
        raise DatasetValidationError("Dataset YAML must contain a mapping.")
    names = config.get("names")
    count = config.get("nc")
    if not isinstance(names, list) or not names or not all(isinstance(name, str) and name.strip() for name in names):
        raise DatasetValidationError("Dataset YAML names must be a non-empty list of class names.")
    if count != len(names):
        raise DatasetValidationError("Dataset class count (nc) must match the names list.")
    for key in ("train", "val"):
        value = config.get(key)
        if not isinstance(value, str) or not value.strip():
            raise DatasetValidationError(f"Dataset YAML must define a non-empty {key} path.")
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = root / candidate
        if not candidate.exists():
            raise DatasetValidationError(f"Dataset {key} path does not exist: {candidate}")
    config["_root"] = str(root)
    config["_yaml_path"] = str(config_path)
    return config
