from pathlib import Path


class OCRUnavailable(Exception):
    pass


def extract_text(path: str, content_type: str) -> str:
    file_path = Path(path)
    if content_type == "application/pdf":
        try:
            import fitz
            with fitz.open(file_path) as pdf:
                text = "\n".join(page.get_text("text") for page in pdf)
            if text.strip():
                return text.strip()
            raise OCRUnavailable("This PDF has no selectable text. OCR for scanned PDFs is not configured on this server.")
        except OCRUnavailable:
            raise
        except Exception as exc:
            raise OCRUnavailable("The PDF could not be read. Please upload another copy.") from exc
    try:
        from PIL import Image
        import pytesseract
        return pytesseract.image_to_string(Image.open(file_path)).strip()
    except Exception as exc:
        raise OCRUnavailable("Image OCR is unavailable. Install the Tesseract OCR engine and try again.") from exc
