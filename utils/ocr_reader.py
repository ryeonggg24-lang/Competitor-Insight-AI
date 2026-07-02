from functools import lru_cache
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import easyocr


@lru_cache(maxsize=1)
def get_reader():
    return easyocr.Reader(["ko", "en"], gpu=False)


def preprocess_image(uploaded_image):
    uploaded_image.seek(0)
    image = Image.open(uploaded_image).convert("RGB")

    # 작은 글씨 인식을 위해 이미지 확대
    width, height = image.size
    image = image.resize((width * 3, height * 3))

    # 선명도/대비 강화
    image = ImageEnhance.Sharpness(image).enhance(2.0)
    image = ImageEnhance.Contrast(image).enhance(1.5)

    # 약한 노이즈 제거
    image = image.filter(ImageFilter.SHARPEN)

    return image


def read_image_text(uploaded_image):
    image = preprocess_image(uploaded_image)
    image_array = np.array(image)

    reader = get_reader()
    results = reader.readtext(
        image_array,
        detail=0,
        paragraph=False
    )

    return "\n".join(results)


def read_images_text(uploaded_images):
    all_text = []

    for image in uploaded_images:
        text = read_image_text(image)
        all_text.append(f"[{image.name}]\n{text}")

    return "\n\n".join(all_text)