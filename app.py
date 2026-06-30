# app.py
import sys
import os
from core.extractor import PDFExtractor
from core.formatter import MarkdownFormatter

def main():
    print("--- Starting PDF Text Extraction ---")
    
    # Check if a PDF file path was provided when running the script
    if len(sys.argv) < 2:
        print("Error: Please provide the path to a PDF file.")
        print("Usage: python app.py path/to/document.pdf")
        return

    pdf_path = sys.argv[1]

    # Quick check to make sure the file actually exists
    if not os.path.exists(pdf_path):
        print(f"Error: The file '{pdf_path}' could not be found.")
        return

    # Step 1: Extract the text content
    print(f"[*] Extracting text from: {pdf_path}...")
    extractor = PDFExtractor(pdf_path)
    raw_text = extractor.extract_text()

    # Step 2: Format the text into clean Markdown structures
    print("[*] Converting text into Markdown format...")
    formatter = MarkdownFormatter(raw_text)
    markdown_output = formatter.format_text()

    # Step 3: Save the finalized Markdown file output
    output_path = "output_structured.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_output)

    print(f"Success! Your Document saved to: {output_path}")

if __name__ == "__main__":
    main()