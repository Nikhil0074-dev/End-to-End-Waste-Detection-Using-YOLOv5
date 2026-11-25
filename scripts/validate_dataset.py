from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main(argv: list[str] | None = None) -> int:
    from config import Settings
    from wasteDetection.components.data_validation import validate_dataset

    parser = argparse.ArgumentParser(description="Validate a waste-detection dataset and its YAML configuration.")
    parser.add_argument("dataset_dir", nargs="?", default=str(Settings.DATASET_DIR))
    parser.add_argument("data_yaml", nargs="?", default=str(Settings.DATA_YAML))
    args = parser.parse_args(argv)

    result = validate_dataset(args.dataset_dir, args.data_yaml)
    print(f"Dataset is valid: {result['_root']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
