# Builder keeps compilers and build-only tools out of the runtime image.
FROM python:3.11-slim-bookworm AS builder
ENV VIRTUAL_ENV=/opt/venv PATH="/opt/venv/bin:$PATH" PIP_NO_CACHE_DIR=1
RUN python -m venv "$VIRTUAL_ENV"
WORKDIR /build
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision && \
    pip install -r requirements.txt

FROM python:3.11-slim-bookworm AS runtime
ENV PATH="/opt/venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN groupadd --system app && useradd --system --gid app --home-dir /app app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app app.py config.py data.yaml ./
COPY --chown=app:app wasteDetection ./wasteDetection
COPY --chown=app:app templates ./templates
COPY --chown=app:app static ./static
RUN mkdir -p /app/model /app/artifacts && chown -R app:app /app
USER app
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "120", "app:app"]
