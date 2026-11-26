from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from config import Settings
from wasteDetection.inference import InferenceError, detect
from wasteDetection.utils.image_utils import ImageInputError, decode_image, encode_image


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Settings)
    if test_config:
        app.config.update(test_config)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/live")
    def live():
        return render_template("live.html")

    @app.get("/api/health")
    def health():
        model_path = app.config["MODEL_PATH"]
        return jsonify(status="ok", model_available=bool(model_path.is_file()))

    @app.post("/predict")
    def predict():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="Request body must be a JSON object."), 400
        try:
            image = decode_image(payload.get("image"))
        except ImageInputError as exc:
            return jsonify(error=str(exc)), 400
        try:
            result = detect(image)
        except FileNotFoundError as exc:
            app.logger.warning("Inference dependency unavailable: %s", exc)
            return jsonify(error="The model or YOLOv5 inference files are not configured."), 503
        except InferenceError:
            app.logger.exception("Inference failed")
            return jsonify(error="Image inference failed."), 500
        except Exception:
            app.logger.exception("Unexpected inference error")
            return jsonify(error="Image inference failed."), 500
        return jsonify(image=encode_image(result))

    @app.errorhandler(413)
    def request_too_large(_error):
        return jsonify(error="Image request exceeds the configured size limit."), 413

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
