from __future__ import annotations

import os
import shutil
import zipfile
from pathlib import Path, PurePosixPath

import gdown


class DataIngestionError(RuntimeError):
    """Raised when dataset download or safe extraction fails."""


def ingest_dataset(file_id: str | None = None, destination: str | Path | None = None) -> Path:
    identifier = file_id or os.getenv("GDRIVE_FILE_ID")
    if not identifier:
        raise DataIngestionError("Set GDRIVE_FILE_ID before downloading the dataset.")
    target = Path(destination or os.getenv("DATASET_DIR", "artifacts/datasets/waste")).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    archive = target.parent / "dataset.zip"
    try:
        downloaded = gdown.download(id=identifier, output=str(archive), quiet=True)
        if not downloaded or not archive.is_file() or archive.stat().st_size == 0:
            raise DataIngestionError("Dataset download returned no usable archive.")
        with zipfile.ZipFile(archive) as bundle:
            for item in bundle.infolist():
                member = PurePosixPath(item.filename)
                if member.is_absolute() or ".." in member.parts or "\\" in item.filename:
                    raise DataIngestionError(f"Unsafe path in dataset archive: {item.filename}")
                if item.file_size > 2 * 1024**3:
                    raise DataIngestionError("Dataset archive contains an oversized file.")
            staging = target.parent / f"{target.name}.extracting"
            if staging.exists():
                shutil.rmtree(staging)
            staging.mkdir(parents=True)
            bundle.extractall(staging)
        if target.exists():
            shutil.rmtree(target)
        staging.replace(target)
        return target
    except (OSError, zipfile.BadZipFile) as exc:
        raise DataIngestionError(f"Unable to download or extract dataset: {exc}") from exc
    finally:
        archive.unlink(missing_ok=True)
