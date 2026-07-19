import fitz  # PyMuPDF
import numpy as np
from pathlib import Path
from typing import List, Dict, Any

from config import SCANNED_PDF_TEXT_THRESHOLD
from ocr.paddle_ocr import extract_text as ocr_extract
from utils.helpers import clean_text

class PDFParser:
    def __init__(self):
        pass

    def parse(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract text from a PDF file. 
        Detects scanned pages based on text length and routes them to OCR.
        """
        results = []
        doc = fitz.open(str(file_path))
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            cleaned_text = clean_text(text)
            
            # Scanned vs digital detection
            if len(cleaned_text) < SCANNED_PDF_TEXT_THRESHOLD:
                # Treat as scanned, route to OCR
                pix = page.get_pixmap(dpi=300) # Use higher DPI for better OCR
                # Convert fitz pixmap to numpy array (OpenCV format)
                # pix.samples contains the raw bytes
                img_array = np.frombuffer(pix.samples, dtype=np.uint8)
                
                if pix.n == 3: # RGB
                    img_array = img_array.reshape(pix.h, pix.w, 3)
                    # Convert RGB to BGR for cv2
                    img_array = img_array[:, :, ::-1]
                elif pix.n == 4: # RGBA
                    img_array = img_array.reshape(pix.h, pix.w, 4)
                    # Convert RGBA to BGRA for cv2
                    img_array = img_array[:, :, [2, 1, 0, 3]]
                elif pix.n == 1: # Grayscale
                    img_array = img_array.reshape(pix.h, pix.w)
                else:
                    # Fallback if unknown color space
                    img_array = img_array.reshape(pix.h, pix.w, pix.n)
                
                ocr_result = ocr_extract(img_array)
                ocr_text = clean_text(ocr_result.get("text", ""))
                
                results.append({
                    "page_number": page_num + 1,
                    "text": ocr_text,
                    "source": "ocr",
                    "ocr_metadata": {
                        "confidence": ocr_result.get("confidence", 0.0),
                        "warning": ocr_result.get("warning")
                    }
                })
            else:
                # Digital page
                results.append({
                    "page_number": page_num + 1,
                    "text": cleaned_text,
                    "source": "digital"
                })
                
        doc.close()
        return results

def parse_pdf(file_path: Path) -> List[Dict[str, Any]]:
    parser = PDFParser()
    return parser.parse(file_path)
