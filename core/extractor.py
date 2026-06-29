# core/extractor.py
import fitz  # This is the PyMuPDF library

class PDFExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path

    def extract_text(self) -> str:
        """Opens a PDF file and extracts all raw text page by page."""
        try:
            # Open the document
            doc = fitz.open(self.pdf_path)
            full_text = []

            # Loop through every single page
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                # Extract text as a single string block
                page_text = page.get_text()
                full_text.append(page_text)
            
            # Join all pages together with line breaks
            return "\n\n".join(full_text)
            
        except Exception as e:
            return f"Error reading PDF: {str(e)}"