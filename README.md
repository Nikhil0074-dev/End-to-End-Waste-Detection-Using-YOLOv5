# Waste Detection System

A Flask-based web application and training pipeline for detecting six waste categories in images: **glass, plastic, metal, paper, cardboard, and trash**. The web server accepts Base64-encoded images, invokes a local YOLOv5 detector with a trained PyTorch checkpoint, and returns an annotated image.

> **Model files are not included in this repository.** The application can start without them, but real predictions require a compatible checkpoint and a YOLOv5 checkout containing `detect.py`.


## Capabilities

- Flask pages at `/` and `/live`.
- Health endpoint at `/api/health`.
- Image inference endpoint at `POST /predict`.
- Base64 image input and annotated Base64 image output.
- Dataset archive download from Google Drive, ZIP extraction, and dataset configuration validation.
- YOLOv5 model training and checkpoint copying to the configured model path.
- Docker image and Docker Compose configuration for running the web application.

## How the application works

### Prediction flow

1. A client sends JSON to `POST /predict` with an `image` property containing raw Base64 or a `data:image/...;base64,...` URL.
2. The server validates and decodes the image, including checking that the decoded content is a readable image.
3. The application writes the input image to a temporary directory and invokes `detect.py` from the configured YOLOv5 directory.
4. YOLOv5 loads the configured checkpoint and produces an annotated image.
5. The server returns that image as Base64 in a JSON response and removes the temporary files.

### Training flow

The training pipeline downloads the dataset ZIP specified by `GDRIVE_FILE_ID`, extracts it, checks the dataset directories and YAML configuration, runs YOLOv5 training, then copies the best checkpoint to `MODEL_PATH`.

Training and inference use local YOLOv5 files; they are not downloaded or vendored by this application. Install the YOLOv5 dependencies appropriate to the checkout and the target machine separately.

## Requirements

### Local development

- Python 3.11 is the version used by the Docker image. The project also uses modern Python syntax, including `str | None` types.
- Dependencies listed in `requirements.txt` for the Flask app, image processing, YAML, dataset download, tests, and linting.
- For inference: a compatible `.pt` checkpoint and a local YOLOv5 repository containing `detect.py`, plus its runtime dependencies.
- For training: a dataset ZIP, Google Drive file ID, a YOLOv5 repository containing `train.py`, PyTorch, and the YOLOv5 training dependencies.

### Docker

- Docker Engine or Docker Desktop with the Compose plugin.
- Local model and YOLOv5 directories mounted into the container for inference.

The Dockerfile creates a CPU-oriented PyTorch environment. GPU inference requires additional host, container runtime, and PyTorch configuration that is not configured by the provided Compose file.

## Local installation and run

Run the following commands from the repository root in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use the Python executable in the virtual environment directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Create a local environment file from the example and edit the values you need:

```powershell
Copy-Item .env.example .env
```

`app.py` does not automatically load `.env` when run directly. Set environment variables in the shell, or use a tool that loads `.env`; Docker Compose reads `.env` as specified in `docker-compose.yml`.

Start the development server:

```powershell
python app.py
```

The app listens on `http://localhost:8080`. Open `http://localhost:8080/` or `http://localhost:8080/live` in a browser. The Flask development server is intended for local development; the Docker image runs the app with Gunicorn.

If the checkpoint or YOLOv5 `detect.py` is absent, the web pages and health endpoint can still run. Predictions return HTTP 503 until the inference dependencies are configured.

## Configuration

Settings are read from environment variables by `config.py`. Paths are interpreted by Python as filesystem paths; relative paths are relative to the process working directory. For Docker Compose, the Compose file supplies container paths for model, YOLOv5, dataset, and YAML configuration.

| Variable | Default | Description |
| --- | --- | --- |
| `SECRET_KEY` | `development-only-change-me` | Flask secret key. Replace it with a unique secret outside local development. |
| `MAX_CONTENT_LENGTH` | `10485760` | Maximum HTTP request size in bytes (10 MiB by default). |
| `MODEL_PATH` | `<project>/model/my_model.pt` | Trained checkpoint used for inference and the destination for the final trained model. |
| `YOLOV5_DIR` | `<project>/yolov5` | Local YOLOv5 checkout. Inference expects `detect.py`; training expects `train.py`. |
| `IMAGE_SIZE` | `416` | Image size passed to YOLOv5 inference and training. |
| `CONFIDENCE_THRESHOLD` | `0.5` | Confidence threshold passed to YOLOv5 inference. |
| `INFERENCE_DEVICE` | Empty | Optional device argument passed to YOLOv5 inference, such as a device identifier supported by YOLOv5. |
| `ALLOWED_ORIGINS` | Empty list | Parsed as a comma-separated list; the current Flask routes do not apply CORS using this setting. |
| `ARTIFACTS_DIR` | `<project>/artifacts` | Root directory for training artifacts and model output. |
| `DATASET_DIR` | `<project>/artifacts/datasets/waste` | Destination directory for the extracted training dataset. |
| `DATA_YAML` | `<project>/data.yaml` | Dataset YAML passed to validation and YOLOv5 training. |
| `GDRIVE_FILE_ID` | Empty | Google Drive file identifier used by the dataset downloader. |
| `TRAIN_EPOCHS` | `10` | Number of epochs passed to YOLOv5 training. |
| `TRAIN_BATCH_SIZE` | `16` | Batch size passed to YOLOv5 training. |
| `TRAIN_WEIGHTS` | `yolov5s.pt` | Initial weights passed to YOLOv5 training. |
| `TRAIN_TIMEOUT` | `86400` seconds | Optional environment variable read by the training component for the training subprocess timeout. |

The `.env.example` file documents common settings. It does not include `ARTIFACTS_DIR` or `TRAIN_TIMEOUT`; those can still be set as environment variables.

### Set environment variables for a local PowerShell session

```powershell
$env:MODEL_PATH = (Resolve-Path .\model\my_model.pt).Path
$env:YOLOV5_DIR = (Resolve-Path .\yolov5).Path
python app.py
```

Adjust the paths for your local layout. Values set with `$env:` apply to the current PowerShell session.

## HTTP API

### `GET /api/health`

Returns HTTP 200 and a JSON object indicating that the web application is responding and whether the configured checkpoint exists.

Example response:

```json
{
  "model_available": false,
  "status": "ok"
}
```

`model_available: true` only indicates that a file exists at `MODEL_PATH`; it does not test whether YOLOv5 can load that file or run inference successfully.

### `POST /predict`

Request JSON must be an object with an `image` property. Supply either raw Base64 or a Base64 data URL:

```json
{
  "image": "data:image/png;base64,iVBORw0KGgo..."
}
```

Example PowerShell request:

```powershell
$imageBase64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes(".\sample.png"))
$payload = @{ image = $imageBase64 } | ConvertTo-Json
$response = Invoke-RestMethod `
  -Uri http://localhost:8080/predict `
  -Method Post `
  -ContentType "application/json" `
  -Body $payload

[IO.File]::WriteAllBytes(
  ".\annotated.png",
  [Convert]::FromBase64String($response.image)
)
```

Successful responses contain the annotated image encoded as Base64:

```json
{
  "image": "<base64-encoded-annotated-image>"
}
```

Common error responses:

| Status | Meaning |
| --- | --- |
| `400` | Request is not a JSON object, image data is missing/invalid, or decoded data is not a readable image. |
| `413` | Request exceeds `MAX_CONTENT_LENGTH`. |
| `503` | Model checkpoint or YOLOv5 inference script is not configured or not found. |
| `500` | Inference subprocess failed or did not produce an annotated image. Check application logs for details. |

## Dataset format and validation

The default `data.yaml` declares six classes:

```yaml
nc: 6
names:
  - glass
  - plastic
  - metal
  - paper
  - cardboard
  - trash
train: images/train
val: images/val
```

The validator checks that:

- The dataset directory and YAML file exist.
- The YAML is a mapping with a non-empty list of class names.
- `nc` equals the number of names.
- Both `train` and `val` paths are configured and exist. Relative paths are checked relative to the dataset directory.

With the default paths, the extracted dataset should include:

```text
artifacts/
└── datasets/
    └── waste/
        └── images/
            ├── train/
            └── val/
```

For object-detection training, each image split also needs the corresponding labels in the format expected by the YOLOv5 checkout. The current validator checks directory and YAML path consistency; it does not inspect image contents or verify label files.

Validate with the configured default paths:

```powershell
python scripts/validate_dataset.py
```

Or provide a dataset directory and YAML file explicitly:

```powershell
python scripts/validate_dataset.py .\artifacts\datasets\waste .\data.yaml
```

The YAML paths must also be meaningful to the YOLOv5 training process, which receives the configured YAML file directly. Verify that its `train` and `val` locations resolve correctly for your dataset and training environment before starting a long training run.

## Training

Training downloads a ZIP archive through `gdown`; set `GDRIVE_FILE_ID` to the Google Drive file ID and ensure the archive can be downloaded by the environment. Configure `DATASET_DIR`, `DATA_YAML`, `YOLOV5_DIR`, and training parameters as needed. Have a YOLOv5 checkout with its training dependencies installed.

From the repository root, run:

```powershell
python -m scripts.train_model
```

The current training script accepts no command-line options; configure paths and parameters with environment variables. The pipeline performs these steps:

1. Downloads the archive to a temporary ZIP file under the dataset parent directory.
2. Extracts the archive into the configured dataset directory.
3. Validates the dataset structure and YAML.
4. Runs YOLOv5 `train.py` with the configured image size, batch size, epochs, YAML, and initial weights.
5. Copies the best training checkpoint to the artifact model output and then to `MODEL_PATH`.

The expected final checkpoint path defaults to `model/my_model.pt`. Training can take significant time and storage, and GPU use depends on your installed YOLOv5/PyTorch environment. The provided Docker Compose setup is for web inference and does not define a training service.

## Docker

### Build and start with Compose

Place your local files beside the Compose project using these paths:

```text
model/my_model.pt
└── yolov5/                 # contains detect.py
```

The Compose configuration expects a directory named `yolov5` (lowercase) containing `detect.py`; the model mount expects `model/my_model.pt`. The runtime image does not copy a model or YOLOv5 source into the image; Compose mounts them from the host.

Build and start the application:

```powershell
docker compose up --pull always --build
```

Open `http://localhost:8080/`. Compose publishes host port `8080` to container port `8080` and mounts `./artifacts` for persistent training artifacts. Stop the service with Ctrl+C or from another terminal:

```powershell
docker compose down
```

### Build and run the image directly

```powershell
docker build -t waste-detection:local .
docker run --rm -p 8080:8080 `
  -v "${PWD}/model:/app/model:ro" `
  -v "${PWD}/yolov5:/app/yolov5:ro" `
  waste-detection:local
```

The image uses Gunicorn, listens on port `8080`, and runs as a non-root user. If no model is mounted at `/app/model/my_model.pt` or the mounted YOLOv5 checkout lacks `detect.py`, prediction requests cannot complete.

### Compose environment values

Compose optionally reads a project `.env` file and sets the paths used inside the container. The Compose `environment` section explicitly sets `MODEL_PATH`, `YOLOV5_DIR`, `DATASET_DIR`, and `DATA_YAML` to container paths. Keep any host-mounted directories and file paths consistent with that configuration.

## Tests and code quality

Run all tests from the project root:

```powershell
pytest
```

The repository's `pytest.ini` configures the project root on the import path and selects `tests/`. The current suite covers Flask page and API behavior, image decoding/encoding, data validation, and dataset CLI behavior. Tests mock model inference where a real checkpoint is not needed.

Run lint checks:

```powershell
python -m flake8 .
```

Compile Python files to check syntax:

```powershell
python -m compileall -q .
```

## Repository layout

```text
.
├── app.py                         Flask routes and app factory
├── config.py                      Environment-based settings
├── data.yaml                      Six-class dataset configuration
├── Dockerfile                     Multi-stage CPU-oriented runtime image
├── docker-compose.yml             Local inference service and mounts
├── requirements.txt               Python application and development dependencies
├── scripts/
│   ├── train_model.py             Training pipeline entry point
│   └── validate_dataset.py        Dataset validation command
├── templates/                     Flask HTML templates
├── static/                        Frontend CSS and JavaScript
├── tests/                         Automated tests
└── wasteDetection/
    ├── components/                Dataset ingestion, validation, and model trainer
    ├── inference.py               YOLOv5 inference subprocess wrapper
    ├── pipeline/                  Training workflow
    └── utils/                     Image input and output helpers
```

## Troubleshooting

### `ModuleNotFoundError` while collecting tests

Run pytest from the repository root, where `pytest.ini` is located:

```powershell
pytest
```

If using a different environment, activate the project virtual environment and reinstall `requirements.txt`.

### Prediction returns HTTP 503

Check that `MODEL_PATH` points to an existing checkpoint and `YOLOV5_DIR` points to a YOLOv5 checkout containing `detect.py`. In Docker, confirm the host paths exist and the mounts point to `/app/model` and `/app/yolov5`.

### Prediction returns HTTP 500

Review the Flask/Gunicorn logs. The endpoint logs the inference exception; the subprocess may fail because of incompatible weights, missing YOLOv5 dependencies, an unsupported device setting, or an invalid Python executable/environment.

### Dataset validation fails

Check that the dataset directory exists, the YAML can be read, `nc` equals the number of class names, and the configured train/validation directories exist. Relative train/validation paths are checked under `DATASET_DIR` by the validator. Also verify path resolution for YOLOv5 training, which reads the configured YAML directly.

### Training cannot download the archive

Check `GDRIVE_FILE_ID`, archive access permissions, network access, and the Google Drive download behavior. Ensure the ZIP is a valid dataset archive with the expected folder layout.

### Port 8080 is already in use

Stop the process already listening on port 8080, or change the host-side port mapping in `docker-compose.yml` (for example, `8081:8080`) and browse to the updated host port.

## Security notes

- Replace the development `SECRET_KEY` before exposing the application outside a local development environment.
- Do not commit `.env`, credentials, model files, or private dataset archives.
- Do not bake secrets into container images. Use environment variables or your deployment platform's secret-management mechanism.
- The API accepts image uploads; keep `MAX_CONTENT_LENGTH` appropriate for your deployment and consider authentication, rate limits, and network restrictions before making the endpoint publicly accessible.
- Run the Flask development server only for local development; use the provided Gunicorn command through the container for a production-style process model.
