import easyocr
import cv2
import numpy as np
from PIL import Image
import io

reader = easyocr.Reader(['en'])

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """Preprocess image for better OCR"""
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    
    # Apply adaptive threshold
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # Morphological operations to clean up
    kernel = np.ones((1, 1), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    return cleaned

def extract_text_from_image(image_bytes: bytes) -> str:
    """Extract text using EasyOCR with preprocessing"""
    try:
        processed_image = preprocess_image(image_bytes)
        
        # Convert back to PIL for EasyOCR
        pil_image = Image.fromarray(processed_image)
        
        # OCR extraction
        results = reader.readtext(np.array(pil_image))
        
        # Combine all detected text
        full_text = " ".join([result[1] for result in results])
        return full_text
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""
