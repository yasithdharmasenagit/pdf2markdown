import fitz

class DocumentChunker:
    """Handles deep layout scanning and segments text layer extractions into balanced data packets."""
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path

    def generate_chunks(self, pages_per_chunk: int = 5) -> list[dict]:
        """
        Parses a PDF text layer and bundles strings into indexed dictionaries.
        Returns a list of structured packets ready for thread pools.
        """
        if pages_per_chunk < 1:
            raise ValueError("Operational parameter error: pages_per_chunk must be 1 or greater.")
            
        chunks = []
        doc = fitz.open(self.pdf_path)
        total_pages = len(doc)
        
        for i in range(0, total_pages, pages_per_chunk):
            start_page = i
            end_page = min(i + pages_per_chunk - 1, total_pages - 1)
            
            chunk_text = ""
            for page_num in range(start_page, end_page + 1):
                page_data = doc[page_num].get_text()
                if page_data:
                    chunk_text += page_data
            
            chunks.append({
                "index": len(chunks),
                "start_p": start_page + 1,
                "end_p": end_page + 1,
                "text": chunk_text
            })
            
        doc.close()
        return chunks