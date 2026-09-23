
import io

from PIL import Image
import pytesseract


# =========================================================
# TESSERACT OCR CONFIGURATION
# =========================================================

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# =========================================================
# EXTRACT TEXT FROM IMAGE
# =========================================================

def extract_text_from_image(file_bytes):

    try:

        image = Image.open(
            io.BytesIO(file_bytes)
        )

        extracted_text = pytesseract.image_to_string(
            image
        )

        return extracted_text.strip()

    except Exception as error:

        return f"OCR processing error: {str(error)}"