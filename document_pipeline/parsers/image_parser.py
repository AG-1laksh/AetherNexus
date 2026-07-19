from pathlib import Path
from typing import Dict, Any
from ocr.paddle_ocr import extract_text as ocr_extract
from utils.helpers import clean_text

class ImageParser:
    def __init__(self):
        pass

    def parse(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract text from an image file using OCR.
        """
        ocr_result = ocr_extract(file_path)
        cleaned_text = clean_text(ocr_result.get("text", ""))
        
        return {
            "text": cleaned_text,
            "source": "ocr",
            "ocr_metadata": {
                "confidence": ocr_result.get("confidence", 0.0),
                "warning": ocr_result.get("warning")
            }
        }

def parse_image(file_path: Path) -> Dict[str, Any]:
    parser = ImageParser()
    return parser.parse(file_path)
