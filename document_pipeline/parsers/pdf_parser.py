import fitz  # PyMuPDF
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
import logging

from config import SCANNED_PDF_TEXT_THRESHOLD
from ocr.paddle_ocr import extract_text as ocr_extract
from utils.helpers import clean_text

logger = logging.getLogger(__name__)

class PDFParser:
    def __init__(self):
        pass

    def parse(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract text from a PDF file. 
        Detects scanned pages based on text length and routes them to OCR.
        """
        file_path = Path(file_path)
        results = []
        try:
            doc = fitz.open(str(file_path))
        except Exception as e:
            logger.error(f"Failed to open PDF {file_path}. It may be corrupted or password-protected: {e}")
            raise ValueError(f"Unable to read PDF file (possibly corrupted or encrypted): {e}")
        
        # Determine if the overall PDF is a standard digital text document vs a scanned document
        sample_pages = min(10, len(doc))
        total_sample_chars = sum(len(clean_text(doc[i].get_text())) for i in range(sample_pages))
        is_scanned_document = (total_sample_chars < 200)
        if is_scanned_document:
            logger.info(f"Document {file_path.name} has minimal digital text ({total_sample_chars} chars in {sample_pages} pages). Enabling OCR mode.")
        else:
            logger.info(f"Document {file_path.name} detected as high-speed digital text PDF ({total_sample_chars} chars across sample pages). Bypassing heavy OCR.")

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            cleaned_text = clean_text(text)
            
            # Scanned vs digital detection (ONLY run OCR if the document as a whole is a scan)
            if is_scanned_document and len(cleaned_text) < SCANNED_PDF_TEXT_THRESHOLD and len(page.get_images()) > 0:
                logger.info(f"Page {page_num+1} appears scanned. Running fast OCR at 150 DPI...")
                # Treat as scanned, route to OCR
                pix = page.get_pixmap(dpi=150) # 150 DPI provides optimal accuracy-to-speed balance on CPU
                img_array = np.frombuffer(pix.samples, dtype=np.uint8)
                
                if pix.n == 3: # RGB
                    img_array = img_array.reshape(pix.h, pix.w, 3)
                    img_array = img_array[:, :, ::-1]
                elif pix.n == 4: # RGBA
                    img_array = img_array.reshape(pix.h, pix.w, 4)
                    img_array = img_array[:, :, [2, 1, 0, 3]]
                elif pix.n == 1: # Grayscale
                    img_array = img_array.reshape(pix.h, pix.w)
                else:
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
                # Digital page (instantaneous extraction without loading PaddleOCR)
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
