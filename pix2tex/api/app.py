# Adapted from https://github.com/kingyiusuen/image-to-latex/blob/main/api/app.py

import binascii
import enum

import PIL
from fastapi import FastAPI
from PIL import Image
from io import BytesIO
from pix2tex.cli import LatexOCR
import base64

model = None
app = FastAPI(title="pix2tex API")


class RetCode(enum.Enum):
    OK = (0, "OK")
    InvalidBase64 = (-1, "Invalid Base64 string")
    InvalidImage = (-2, "Invalid Image")
    InternalError = (-3, "Internal Error")


def read_imagefile(file) -> Image.Image:
    image = Image.open(BytesIO(file))
    return image


@app.on_event("startup")
async def load_model():
    global model
    if model is None:
        model = LatexOCR()


@app.get("/")
def root():
    """Health check."""
    c, m = RetCode.OK.value
    response = {"code": c, "msg": m, "data": {}}
    return response


@app.get("/predict")
def predict(img: str):
    """Predict the Latex code from an image file.

    Args:
        img Base64 encoded str with ascii code

    Returns:
        json result
    """
    global model
    try:
        arr = base64.urlsafe_b64decode(img)
        img = Image.open(BytesIO(arr))
        latex = model(img)
        c, m = RetCode.OK.value
        response = {"code": c, "msg": m, "data": {"latex": latex}}
        return response
    except binascii.Error:
        c, m = RetCode.InvalidBase64.value
        response = {"code": c, "msg": m, "data": {}}
        return response
    except PIL.UnidentifiedImageError:
        c, m = RetCode.InvalidImage.value
        response = {"code": c, "msg": m, "data": {}}
        return response
    except:  # noqa: E722
        c, m = RetCode.InternalError.value
        response = {"code": c, "msg": m, "data": {}}
        return response

# @app.post('/predict/')
# async def predict(file: UploadFile = File(...)) -> str:
#     """Predict the Latex code from an image file.

#     Args:
#         file (UploadFile, optional): Image to predict. Defaults to File(...).

#     Returns:
#         str: Latex prediction
#     """
#     global model
#     image = Image.open(file.file)
#     return model(image)


# @app.post('/bytes/')
# async def predict_from_bytes(file: bytes = File(...)) -> str:  # , size: str = Form(...)
#     """Predict the Latex code from a byte array

#     Args:
#         file (bytes, optional): Image as byte array. Defaults to File(...).

#     Returns:
#         str: Latex prediction
#     """
#     global model
#     #size = tuple(int(a) for a in size.split(','))
#     image = Image.open(BytesIO(file))
#     return model(image, resize=False)