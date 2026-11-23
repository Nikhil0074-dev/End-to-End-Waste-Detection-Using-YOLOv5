# model/

Place your trained weights here as `my_model.pt`.

This is the file `app.py` loads for the `/predict` route (see `BASE_MODEL_PATH`
in `wasteDetection/constant/__init__.py`). After running the `/train` route or
`python wasteDetection/pipeline/training_pipeline.py`, the best checkpoint from
YOLOv5 training is copied here automatically.

You can also drop in the stock `yolov5s.pt` weights (downloaded automatically
by YOLOv5 on first run) to try the app before training a custom model.
