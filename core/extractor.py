import os
import fitz

class PDFExtractor:
    """Reads deep structural text blocks from a disk address with explicit system fault alerting."""
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Extraction Target Missing: Path location does not exist at '{pdf_path}'")

    def extract_text(self) -> str:
        """Extracts the entire document text layer with strict error propagation metrics."""
        try:
            doc = fitz.open(self.pdf_path)
            
            if doc.is_encrypted:
                raise PermissionError(f"Extraction Blocked: '{os.path.basename(self.pdf_path)}' is locked with security encryption credentials.")
                
            full_text = []
            for page in doc:
                text_content = page.get_text()
                full_text.append(text_content)
                
            doc.close()
            return "\n\n".join(full_text)
            
        except fitz.FileDataError:
            raise ValueError(f"Corrupted File Engine Alert: PyMuPDF could not parse document structural contents at '{self.pdf_path}'")
        except Exception as e:
            # Propagate the actual trace up the call stack instead of hiding it
            raise RuntimeError(f"OS Resource Extraction Failure on target file: {str(e)}")