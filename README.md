#  End-to-End Waste Detection Using YOLOv5

An end-to-end object detection system that classifies waste items (glass,plastic, metal, paper, cardboard, trash) from images or a live camera feed,built around a YOLOv5s model, a Flask web app, a modular training pipeline,and a CI/CD deployment path to AWS.

## Architecture

```
User Interface Layer
   Web Browser  ─────────────►  Flask Web App (app.py)
                                   "/"        Home Route (index.html)
                                   "/train"   Training Route
                                   "/predict" Prediction Route (Base64 image I/O)
                                   "/live"    Live Camera Detection

Training Pipeline (TrainPipeline)
   Data Ingestion   → download from Google Drive, extract zip → DataIngestionArtifact
   Data Validation  → validate train/valid/data.yaml, write status → DataValidationArtifact
   Model Trainer    → configure YOLOv5s yaml, train, save best.pt → ModelTrainerArtifact

Core Package Structure (wasteDetection/)
   entity/       Config + Artifacts dataclasses
   constant/     URLs, paths, hyperparameters
   utils/        main_utils (decodeImage, encodeImageIntoBase64, read_yaml_file, ...)
   logger/       cross-cutting logging
   exception/    cross-cutting exception handling

CI/CD & Deployment
   GitHub Actions → lint / test  →  AWS ECR (build & push)  →  AWS EC2 self-hosted runner  →  Docker
```

## Project layout

```
wasteDetection/
├── app.py                          # Flask app: "/", "/train", "/predict", "/live"
├── setup.py
├── requirements.txt
├── data.yaml                       # YOLOv5 class + path config
├── Dockerfile
├── .github/workflows/main.yaml     # CI/CD pipeline
├── templates/
│   ├── index.html                  # upload + scan UI
│   └── live.html                   # webcam UI
├── static/
│   ├── css/style.css
│   └── js/{main.js, live.js}
├── data/                           # train/, valid/, data.yaml (populated by pipeline)
├── model/                          # trained weights land here (my_model.pt)
├── tests/
└── wasteDetection/
    ├── entity/
    │   ├── config_entity.py        # DataIngestionConfig, DataValidationConfig, ModelTrainerConfig
    │   └── artifacts_entity.py     # DataIngestionArtifact, DataValidationArtifact, ModelTrainerArtifact
    ├── constant/                   # URLs, paths, hyperparameters
    ├── utils/main_utils.py         # decodeImage, encodeImageIntoBase64, yaml helpers
    ├── logger/                     # rotating file + console logger
    ├── exception/                  # WasteDetectionException
    ├── components/
    │   ├── data_ingestion.py
    │   ├── data_validation.py
    │   └── model_trainer.py
    └── pipeline/
        └── training_pipeline.py    # orchestrates the 3 components above
```

## Getting started

### 1. Clone & install

```bash
git clone https://github.com/Nikhil0074-dev/End-to-End-Waste-Detection-Using-YOLOv5
cd wasteDetection
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Get YOLOv5 (used for training + inference under the hood)

```bash
git clone https://github.com/ultralytics/yolov5.git
pip install -r yolov5/requirements.txt
```

### 3. Configure your dataset source

Edit `GDRIVE_FILE_ID` in `wasteDetection/constant/__init__.py` to point at
your zipped dataset (YOLOv5-format: `train/`, `valid/`, `data.yaml`) hosted
on Google Drive.

### 4. Run the training pipeline

Either via the web route:

```bash
python app.py
# then visit http://localhost:8080/train
```

or directly:

```bash
python wasteDetection/pipeline/training_pipeline.py
```

This runs **Data Ingestion → Data Validation → Model Trainer**, and copies
the resulting `best.pt` into `model/my_model.pt`.

### 5. Run the app

```bash
python app.py
```

- `/` — upload an image and run detection
- `/train` — trigger the training pipeline
- `/predict` — POST `{ "image": "<base64>" }`, returns `{ "image": "<base64>" }`
- `/live` — webcam-based live detection

## Docker

```bash
docker build -t waste-detection .
docker run -p 8080:8080 waste-detection
```

## CI/CD

`.github/workflows/main.yaml` runs three jobs on push to `main`:

1. **Continuous Integration** — lint + test
2. **Build & Push** — builds the Docker image and pushes it to AWS ECR
3. **Continuous Deployment** — a self-hosted EC2 runner pulls the latest
   image and restarts the container

Required repository secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`,
`AWS_REGION`, `ECR_REPOSITORY_NAME`.

## Tech stack

Flask · Flask-CORS · YOLOv5 (PyTorch) · OpenCV · gdown · PyYAML · Docker ·
GitHub Actions · AWS ECR/EC2
