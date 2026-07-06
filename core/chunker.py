# core/chunker.py
import fitz
from core.extractor import PDFExtractor

class DocumentChunker:
    """Handles deep layout scanning and segments text layer extractions into balanced data packets."""
    def __init__(self, pdf_path: str, use_ocr: bool = False):
        self.pdf_path = pdf_path
        self.use_ocr = use_ocr

    def generate_chunks(self, pages_per_chunk: int = 5) -> list[dict]:
        """
        Extracts structured page tokens and bundles pages into group segments.
        Returns serialized collections containing text strings and layout metadata.
        """
        if pages_per_chunk < 1:
            raise ValueError("Operational parameter error: pages_per_chunk must be 1 or greater.")
            
        extractor = PDFExtractor(self.pdf_path, use_ocr=self.use_ocr)
        # Pull layout-aware text lists from the document
        structured_data = extractor.extract_text()
        total_pages = len(structured_data)
        chunks = []
        
        for i in range(0, total_pages, pages_per_chunk):
            start_page = i
            end_page = min(i + pages_per_chunk - 1, total_pages - 1)
            
            # Slice the structured page lists for this chunk
            chunk_pages_subset = structured_data[start_page:end_page + 1]
            
            # Generate a plain text layout representation for the LLM context prompt
            raw_text_prompt = ""
            for page_blocks in chunk_pages_subset:
                for block in page_blocks:
                    line_strings = [line["text"] for line in block]
                    raw_text_prompt += " ".join(line_strings) + "\n"
                raw_text_prompt += "\n"

            chunks.append({
                "index": len(chunks),
                "start_p": start_page + 1,
                "end_p": end_page + 1,
                "structured_data": chunk_pages_subset,
                "text": raw_text_prompt
            })
            
        return chunks