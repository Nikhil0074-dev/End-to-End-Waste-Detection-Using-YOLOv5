from __future__ import annotations

import base64
import binascii
import io
import re

from PIL import Image, UnidentifiedImageError

_DATA_URL = re.compile(r"^data:image/[a-zA-Z0-9.+-]+;base64,(.*)$", re.DOTALL)


class ImageInputError(ValueError):
    """Raised when submitted image data is missing, malformed, or unreadable."""


def decode_image(value: object) -> bytes:
    if not isinstance(value, str) or not value.strip():
        raise ImageInputError("A non-empty Base64 image string is required.")
    match = _DATA_URL.match(value.strip())
    encoded = match.group(1) if match else value.strip()
    try:
        data = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ImageInputError("Image data must be valid Base64.") from exc
    if not data:
        raise ImageInputError("Image data is empty.")
    try:
        with Image.open(io.BytesIO(data)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ImageInputError("Decoded data is not a supported image.") from exc
    return data


def encode_image(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")
