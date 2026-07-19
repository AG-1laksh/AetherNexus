import docx
from pathlib import Path
from typing import List, Dict, Any

from utils.helpers import clean_text

class DOCXParser:
    def __init__(self):
        pass

    def parse(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract text from a DOCX file.
        Preserves heading styles by formatting them as Markdown headers.
        """
        doc = docx.Document(str(file_path))
        extracted_paragraphs = []
        
        for p in doc.paragraphs:
            text = clean_text(p.text)
            if not text:
                continue
                
            style_name = p.style.name if p.style else ""
            
            # Preserve headings using Markdown syntax
            if style_name.startswith('Heading'):
                try:
                    level = int(style_name.split(' ')[-1])
                    prefix = '#' * level + ' '
                except ValueError:
                    prefix = '# '
                
                text = f"{prefix}{text}"
            
            extracted_paragraphs.append(text)
            
        full_text = "\n\n".join(extracted_paragraphs)
        
        return [{
            "text": full_text,
            "source": "digital"
        }]

def parse_docx(file_path: Path) -> List[Dict[str, Any]]:
    parser = DOCXParser()
    return parser.parse(file_path)
