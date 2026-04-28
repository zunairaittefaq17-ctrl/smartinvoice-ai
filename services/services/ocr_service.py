import pytesseract
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

def extract_text_from_image(image_bytes: bytes) -> str:
    """Lightweight OCR using pytesseract"""
    try:
        # Load image
        image = Image.open(io.BytesIO(image_bytes))
        
        # OCR with optimized config
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz@#$%€£.,:;()-+/ '
        
        text = pytesseract.image_to_string(image, config=custom_config)
        logger.info(f"OCR extracted {len(text)} characters")
        return text.strip()
        
    except Exception as e:
        logger.error(f"OCR failed: {str(e)}")
        return ""
