# app.py
import sys
import os
from core.extractor import PDFExtractor

def main():
    print("--- Starting PDF Text Extraction ---")
    
    # Check if a PDF file path was provided when running the script
    if len(sys.argv) < 2:
        print("❌ Error: Please provide the path to a PDF file.")
        print("Usage: python app.py path/to/document.pdf")
        return

    pdf_path = sys.argv[1]

    # Quick check to make sure the file actually exists
    if not os.path.exists(pdf_path):
        print(f"❌ Error: The file '{pdf_path}' could not be found.")
        return

    print(f"[*] Extracting text from: {pdf_path}...")
    
    # Initialize our extractor module
    extractor = PDFExtractor(pdf_path)
    extracted_text = extractor.extract_text()

    # Define our output file name
    output_path = "output_raw_text.txt"

    # Save the extracted text to a file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    print(f"✅ Success! Raw text saved to: {output_path}")

if __name__ == "__main__":
    main()