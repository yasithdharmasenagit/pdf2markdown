# core/formatter.py

class MarkdownFormatter:
    def __init__(self, raw_text: str):
        self.raw_text = raw_text

    def format_text(self) -> str:
        """Processes raw text line-by-line and applies basic Markdown structures."""
        if not self.raw_text.strip():
            return "*[No text extracted from document]*"

        lines = self.raw_text.splitlines()
        markdown_lines = []
        
        for line in lines:
            cleaned_line = line.strip()
            
            # Skip completely empty lines to reduce clutter
            if not cleaned_line:
                continue
                
            # Basic Rule: If a line is short, completely UPPERCASE, and doesn't end with a period,
            # we can guess it's a structural document heading!
            if len(cleaned_line) < 50 and cleaned_line.isupper() and not cleaned_line.endswith('.'):
                markdown_lines.append(f"\n## {cleaned_line.title()}\n")
            else:
                # Otherwise, treat it as a standard paragraph line
                markdown_lines.append(cleaned_line)

        # Join everything back together, using clean spacing between structural parts
        return "\n".join(markdown_lines)