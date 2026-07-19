import re

def clean_text(text: str) -> str:
    """
    Cleans extracted text by removing empty lines, collapsing repeated whitespace,
    and stripping common PDF page artifacts (like standalone page numbers),
    while preserving headings.
    """
    if not text:
        return ""

    cleaned_lines = []
    lines = text.split('\n')
    
    for line in lines:
        # Strip leading/trailing whitespaces
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Strip simple page artifacts (standalone numbers often found at top/bottom of pages)
        # e.g., "12", "- 12 -", "Page 12"
        if re.match(r'^[-—\s]*\d+[-—\s]*$', line) or re.match(r'^Page\s+\d+$', line, re.IGNORECASE):
            continue
            
        # Collapse multiple spaces into a single space (while keeping the line intact)
        line = re.sub(r'[ \t]+', ' ', line)
        
        cleaned_lines.append(line)

    # Rejoin lines. Consecutive newlines were removed by skipping empty lines.
    return '\n'.join(cleaned_lines)

def get_file_extension(filename: str) -> str:
    """Extracts the extension from a filename in lowercase."""
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[-1].lower()

def sanitize_filename(filename: str) -> str:
    """Removes unsafe characters from a filename."""
    return re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)

