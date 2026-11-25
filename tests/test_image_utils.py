import base64
import io

import pytest
from PIL import Image

from wasteDetection.utils.image_utils import ImageInputError, decode_image, encode_image


def sample_png():
    stream = io.BytesIO()
    Image.new("RGB", (2, 2)).save(stream, format="PNG")
    return stream.getvalue()


def test_decode_raw_base64_and_data_url():
    data = sample_png()
    assert decode_image(base64.b64encode(data).decode()) == data
    assert decode_image("data:image/png;base64," + base64.b64encode(data).decode()) == data


def test_encode_image_round_trip():
    data = sample_png()
    assert base64.b64decode(encode_image(data)) == data


@pytest.mark.parametrize("value", [None, "", "not-base64!", base64.b64encode(b"not an image").decode()])
def test_invalid_images_raise(value):
    with pytest.raises(ImageInputError):
        decode_image(value)
