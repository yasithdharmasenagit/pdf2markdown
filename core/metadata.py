import fitz

class DocumentMetadataParser:
    """Extracts internal binary attributes, properties, and structural TOC outlines."""
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path

    def generate_frontmatter_and_toc(self) -> str:
        """Compiles YAML header markers and structured Table of Contents from internal bookmarks."""
        try:
            doc = fitz.open(self.pdf_path)
            meta = doc.metadata or {}
            toc = doc.get_toc()
            
            # 1. Build YAML Frontmatter header
            lines = ["---"]
            lines.append(f"title: \"{meta.get('title', 'Untitled Document').replace('&quot;', '')}\"")
            lines.append(f"author: \"{meta.get('author', 'Unknown Author')}\"")
            lines.append(f"subject: \"{meta.get('subject', 'Document Conversion Output')}\"")
            lines.append("--- \n")
            
            # 2. Build Internal Bookmark Outlines if populated
            if toc:
                lines.append("# Table of Contents\n")
                for level, title, page in toc:
                    indentation = "  " * (level - 1)
                    lines.append(f"{indentation}- [{title}](#page-{page})")
                lines.append("\n---\n")
                
            doc.close()
            return "\n".join(lines)
        except Exception as e:
            return f"\n"