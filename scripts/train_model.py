from __future__ import annotations

import argparse

from wasteDetection.pipeline.training_pipeline import run_training_pipeline


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download data, validate it, and train the waste detector.")
    parser.parse_args()
    print(f"Training complete. Model: {run_training_pipeline()}")
