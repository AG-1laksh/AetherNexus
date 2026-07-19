import logging
import cv2
import numpy as np
from pathlib import Path
from typing import Union, Dict, Any, Optional

try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

from config import OCR_CONFIDENCE_THRESHOLD

logger = logging.getLogger(__name__)

class PaddleOCREngine:
    def __init__(self):
        self.ocr = None
        if PADDLE_AVAILABLE:
            try:
                # Initialize PaddleOCR
                self.ocr = PaddleOCR(use_angle_cls=True, lang='en')
            except Exception as e:
                logger.error(f"Failed to initialize PaddleOCR: {e}")
                self.ocr = None

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Applies grayscale and contrast normalization."""
        # Convert to grayscale if it's a color image
        if len(image.shape) == 3 and image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif len(image.shape) == 3 and image.shape[2] == 4: # RGBA
            gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
        else:
            gray = image.copy()
            
        # Apply contrast normalization (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        norm_img = clahe.apply(gray)
        return norm_img

    def _run_pytesseract(self, image: np.ndarray) -> Dict[str, Any]:
        """Fallback to PyTesseract."""
        if not PYTESSERACT_AVAILABLE:
            logger.warning("PyTesseract is not available for fallback.")
            return {"text": "", "confidence": 0.0, "source": "none", "warning": "All OCR engines failed"}
        
        logger.info("Using PyTesseract as fallback.")
        try:
            # We don't get per-word confidence easily from basic image_to_string without image_to_data
            # We'll just extract text and give a default confidence
            text = pytesseract.image_to_string(image)
            return {
                "text": text.strip(),
                "confidence": 0.5, # Default arbitrary confidence for basic tesseract string
                "source": "pytesseract",
                "warning": "Fallback engine used"
            }
        except Exception as e:
            logger.error(f"PyTesseract fallback failed: {e}")
            return {"text": "", "confidence": 0.0, "source": "none", "warning": f"PyTesseract failed: {e}"}

    def _run_paddleocr(self, image: np.ndarray) -> Optional[Dict[str, Any]]:
        """Run paddle OCR on an image numpy array."""
        if self.ocr is None:
            raise RuntimeError("PaddleOCR engine is not initialized.")
            
        result = self.ocr.ocr(image)
        if not result:
            return {"text": "", "confidence": 0.0, "source": "paddleocr"}

        extracted_text = []
        confidences = []
        
        for res_dict in result:
            if isinstance(res_dict, dict):
                texts = res_dict.get('rec_texts', [])
                scores = res_dict.get('rec_scores', [])
                extracted_text.extend(texts)
                confidences.extend(scores)

        full_text = "\n".join(extracted_text)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            "text": full_text,
            "confidence": avg_confidence,
            "source": "paddleocr"
        }

    def extract_text(self, image_input: Union[str, Path, np.ndarray]) -> Dict[str, Any]:
        """
        Extract text from an image.
        image_input can be a file path or a numpy array (cv2 image).
        """
        if isinstance(image_input, (str, Path)):
            image = cv2.imread(str(image_input))
            if image is None:
                return {"text": "", "confidence": 0.0, "warning": "Failed to read image file."}
        else:
            image = image_input

        # Try PaddleOCR first
        try:
            res = self._run_paddleocr(image)
            
            # If confidence is low or no text, try with preprocessed image
            if res and (res['confidence'] < OCR_CONFIDENCE_THRESHOLD or not res['text'].strip()):
                logger.info("Raw OCR confidence low or empty. Applying preprocessing...")
                preprocessed = self._preprocess_image(image)
                res_prep = self._run_paddleocr(preprocessed)
                
                # Keep the preprocessed result if it's better
                if res_prep and res_prep['confidence'] > res['confidence']:
                    res = res_prep
                    
            if res:
                if res['confidence'] < OCR_CONFIDENCE_THRESHOLD:
                    res['warning'] = f"Low confidence: {res['confidence']:.2f}"
                return res

        except Exception as e:
            logger.error(f"PaddleOCR raised an exception: {e}")
            
        # Fallback to PyTesseract
        return self._run_pytesseract(image)

# Singleton instance for easy import
ocr_engine = PaddleOCREngine()

def extract_text(image_input: Union[str, Path, np.ndarray]) -> Dict[str, Any]:
    return ocr_engine.extract_text(image_input)
