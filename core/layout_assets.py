import os
import fitz

class LayoutAssetManager:
    """Detects, extracts, and serializes embedded tables and image assets from page coordinates."""
    def __init__(self, pdf_path: str, output_image_dir: str = "utils/output/images"):
        self.pdf_path = pdf_path
        self.output_image_dir = output_image_dir
        os.makedirs(self.output_image_dir, exist_ok=True)

    def extract_page_tables(self, page) -> list[dict]:
        """Finds tabular grids on a page and returns them formatted as clean Markdown strings."""
        markdown_tables = []
        try:
            tables = page.find_tables()
            for i, table in enumerate(tables):
                extracted_matrix = table.extract()
                if not extracted_matrix or len(extracted_matrix) < 1:
                    continue
                
                # Build Markdown structural rows
                headers = [str(cell or "").strip().replace("\n", " ") for cell in extracted_matrix[0]]
                separator = ["---"] * len(headers)
                
                md_lines = [
                    "| " + " | ".join(headers) + " |",
                    "| " + " | ".join(separator) + " |"
                ]
                
                for row in extracted_matrix[1:]:
                    clean_row = [str(cell or "").strip().replace("\n", " ") for cell in row]
                    md_lines.append("| " + " | ".join(clean_row) + " |")
                
                markdown_tables.append({
                    "bbox": table.bbox,
                    "markdown": "\n".join(md_lines) + "\n"
                })
        except Exception:
            pass # Graceful bypass if PyMuPDF version constraints restrict table search
        return markdown_tables

    def extract_page_images(self, doc, page, page_index: int) -> list[dict]:
        """Saves embedded images to disk and generates relative image markdown reference markers."""
        image_references = []
        try:
            image_list = page.get_images(full=True)
            for img_idx, img_meta in enumerate(image_list):
                xref = img_meta[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                filename = f"img_p{page_index + 1}_{img_idx + 1}.{image_ext}"
                filepath = os.path.join(self.output_image_dir, filename)
                
                with open(filepath, "wb") as f:
                    f.write(image_bytes)
                
                # Estimate a visual layout bounding box or placement anchor
                rects = page.get_image_rects(xref)
                bbox = rects[0] if rects else (0, 0, 0, 0)
                
                image_references.append({
                    "bbox": bbox,
                    "markdown": f"\n\n![](images/{filename})\n\n"
                })
        except Exception:
            pass
        return image_references