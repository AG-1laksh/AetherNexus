import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from chunking.chunk import chunk_document, DocumentChunk

def main():
    print("=== Testing Chunking Algorithm ===\n")
    
    # Generate some long dummy text to test boundaries
    dummy_text = (
        "This is the first sentence. It is relatively short. "
        "Here is a second sentence that adds a bit more length to the paragraph, "
        "but still isn't too long. "
        "Now we will add a very long sentence that just keeps going and going and going, "
        "with multiple clauses, because we want to test how the chunker handles a significant "
        "amount of text without a sentence break, ensuring that we eventually hit the chunk "
        "size limit or at least get close to it before the next sentence boundary appears. "
        "This is an extra sentence to push the boundary further. "
        "What happens when we add even more sentences? We need enough text to exceed the 800 "
        "character limit so we can observe the overlap in action! Let's just repeat this text. "
    ) * 4  # Repeat to make it very long
    
    dummy_text += "\n\nThis is a new paragraph. It should be handled gracefully."
    
    pages = [
        {
            "page_number": 1,
            "text": dummy_text,
            "source": "digital"
        }
    ]
    
    print(f"Total input characters: {len(dummy_text)}")
    
    chunks = chunk_document(pages, filename="test_doc.txt", document_type="txt")
    
    print(f"Total chunks generated: {len(chunks)}\n")
    
    print("=== Sample Chunks ===")
    for i, c in enumerate(chunks[:3]):  # Print up to 3 chunks
        print(f"Chunk {i+1}:")
        print(f"  ID: {c.chunk_id}")
        print(f"  Page: {c.page_number}")
        print(f"  Char Count: {c.char_count}")
        print(f"  Text: {c.text}\n")
        
    print("=== Overlap Verification ===")
    if len(chunks) >= 2:
        c1 = chunks[0].text
        c2 = chunks[1].text
        
        # Get the last 100 characters of chunk 1
        end_of_c1 = c1[-100:]
        print(f"Last ~100 chars of Chunk 1:\n'{end_of_c1}'\n")
        
        start_of_c2 = c2[:100]
        print(f"First ~100 chars of Chunk 2:\n'{start_of_c2}'\n")
        
        # Check if they match. Note: The chunker snaps to the first space, so they might not be exactly 100 chars identical, 
        # but the starting words of chunk 2 should be in the end of chunk 1.
        print("Overlap is working correctly if the text above matches!")
    else:
        print("Not enough chunks generated to test overlap.")

if __name__ == "__main__":
    main()
