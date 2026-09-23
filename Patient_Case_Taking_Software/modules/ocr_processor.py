import io
import shutil

import pytesseract
from PIL import Image


def extract_text_from_image(image_bytes):
    """
    Extract text from an uploaded image.
    Supports Windows locally and Linux cloud deployment.
    """

    try:
        if not image_bytes:
            return "No image was uploaded."

        image = Image.open(io.BytesIO(image_bytes))

        # Find Tesseract automatically from the system PATH.
        # Works with Linux cloud deployment.
        tesseract_path = shutil.which("tesseract")

        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

        else:
            # Windows local installation fallback
            windows_path = (
                r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            )

            if shutil.which(windows_path):
                pytesseract.pytesseract.tesseract_cmd = windows_path

            else:
                return (
                    "OCR engine not found. "
                    "Install Tesseract OCR and check packages.txt."
                )

        extracted_text = pytesseract.image_to_string(
            image,
            config="--psm 6"
        )

        extracted_text = extracted_text.strip()

        if not extracted_text:
            return "No readable text found in the image."

        return extracted_text

    except Exception as error:
        return f"OCR Processing Error: {str(error)}"
