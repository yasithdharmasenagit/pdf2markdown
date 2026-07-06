import os
import re
from collections import Counter
import fitz

class PDFExtractor:
    """Advanced layout-aware PDF text extraction suite with automated OCR fallback capability."""
    def __init__(self, pdf_path: str, use_ocr: bool = False):
        self.pdf_path = pdf_path
        self.use_ocr = use_ocr
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Extraction Target Missing: Path location does not exist at '{pdf_path}'")

    def _identify_running_headers_footers(self, doc) -> set:
        """Samples the boundaries of all pages to discover repeating header/footer sequences."""
        header_candidates = []
        footer_candidates = []
        total_pages = len(doc)
        
        if total_pages < 3:
            return set() # Not enough data pool to calculate frequencies

        for page in doc:
            blocks = page.get_text("blocks")
            if not blocks:
                continue
            # Sort blocks vertically to find absolute top and bottom elements
            sorted_blocks = sorted(blocks, key=lambda b: b[1])
            
            if sorted_blocks:
                # Top block (Header candidate)
                top_text = sorted_blocks[0][4].strip()
                if top_text and not re.search(r'^\d+$', top_text):
                    header_candidates.append(top_text)
                    
                # Bottom block (Footer candidate)
                bottom_text = sorted_blocks[-1][4].strip()
                if bottom_text and not re.search(r'^\d+$', bottom_text):
                    footer_candidates.append(bottom_text)

        # Lines repeating on >= 65% of the document are flagged as structural layout noise
        threshold = total_pages * 0.65
        headers_to_strip = {text for text, count in Counter(header_candidates).items() if count >= threshold}
        footers_to_strip = {text for text, count in Counter(footer_candidates).items() if count >= threshold}
        
        return headers_to_strip.union(footers_to_strip)

    def extract_text(self) -> str:
        """Parses the layout structure of the document, strips headers/footers, and uses OCR if needed."""
        try:
            doc = fitz.open(self.pdf_path)
            if doc.is_encrypted:
                raise PermissionError(f"Extraction Blocked: '{os.path.basename(self.pdf_path)}' is encrypted.")

            global_noise_artifacts = self._identify_running_headers_footers(doc)
            compiled_document_text = []

            # Page Number regular expression rules matching: "Page 1", "1 of 10", or standalone digits
            page_num_regex = re.compile(r'(?i)^\s*page\s+\d+(\s+of\s+\d+)?\s*$|^\s*\d+\s*$')

            for page_index, page in enumerate(doc):
                page_text_output = []
                # Fetch structured dict representation containing block positions and spans
                page_dict = page.get_text("dict")
                blocks = page_dict.get("blocks", [])

                # Filter text blocks and separate them from image blocks
                text_blocks = [b for b in blocks if "lines" in b]

                # --- OCR FALLBACK LOGIC ---
                if not text_blocks or sum(len(l.get("spans", [])) for b in text_blocks for l in b.get("lines", [])) < 10:
                    if self.use_ocr:
                        try:
                            # Try built-in OCR wrapper if available, else fallback to standard extraction
                            ocr_text = page.get_text("text", flags=fitz.TEXTFLAGS_SEARCH)
                            if len(ocr_text.strip()) > 10:
                                page_text_output.append(ocr_text)
                            else:
                                # Render the page layout as an image to run OCR
                                pix = page.get_pixmap(dpi=150)
                                ocr_text = page.get_textpage_ocr().get_text()
                                page_text_output.append(ocr_text)
                        except Exception:
                            # Safely handle environments missing underlying Tesseract binaries
                            pass
                    if not page_text_output:
                        compiled_document_text.append("")
                        continue

                # --- MULTI-COLUMN DETECTOR & STRUCTURAL SORTING ---
                # Cluster blocks into column channels based on horizontal x0 boundaries
                columns = []
                # Sort left-to-right first
                sorted_by_x = sorted(text_blocks, key=lambda b: b["bbox"][0])
                
                for block in sorted_by_x:
                    x0 = block["bbox"][0]
                    placed = False
                    for col in columns:
                        # If a block fits within 80 pixels of an existing column cluster, group them
                        if abs(col["x0_avg"] - x0) < 80:
                            col["blocks"].append(block)
                            col["x0_avg"] = sum(b["bbox"][0] for b in col["blocks"]) / len(col["blocks"])
                            placed = True
                            break
                    if not placed:
                        columns.append({"x0_avg": x0, "blocks": [block]})

                # Sort column channels from left to right, then sort blocks top-to-bottom within each column
                sorted_columns = sorted(columns, key=lambda c: c["x0_avg"])
                
                for column in sorted_columns:
                    sorted_blocks = sorted(column["blocks"], key=lambda b: b["bbox"][1])
                    
                    for block in sorted_blocks:
                        block_lines = []
                        for line in block["lines"]:
                            line_text = "".join([span["text"] for span in line["spans"]]).strip()
                            
                            # Skip matched header/footer elements or dynamic page numbers
                            if line_text in global_noise_artifacts or page_num_regex.match(line_text):
                                continue
                                
                            if line_text:
                                # Calculate text features using the first span's styling metrics
                                first_span = line["spans"][0]
                                size = first_span.get("size", 10.0)
                                flags = first_span.get("flags", 0)
                                is_bold = bool(flags & 2) # Bit flag check for bold styles
                                
                                block_lines.append({
                                    "text": line_text,
                                    "size": size,
                                    "bold": is_bold
                                })
                        
                        if block_lines:
                            page_text_output.append(block_lines)

                compiled_document_text.append(page_text_output)

            doc.close()
            return compiled_document_text
            
        except Exception as e:
            raise RuntimeError(f"Advanced Extraction Failure: {str(e)}")