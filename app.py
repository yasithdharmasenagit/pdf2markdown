import sys
import os
from core.extractor import PDFExtractor
from core.formatter import MarkdownFormatter
from providers import GeminiProvider  # Updated package import!

def main():
    print("--- Starting PDF to Markdown AI Conversion Pipeline ---")
    
    if len(sys.argv) < 2:
        print("Error: Please provide the path to a PDF file.")
        print("Usage: python app.py path/to/document.pdf")
        return

    pdf_path = sys.argv[1]

    if not os.path.exists(pdf_path):
        print(f"Error: The file '{pdf_path}' could not be found.")
        return

    # Step 1: Extract the text content from PDF
    print(f"[*] Step 1: Extracting text from {pdf_path}...")
    extractor = PDFExtractor(pdf_path)
    raw_text = extractor.extract_text()

    # Step 2: Check for Gemini API key to decide execution route
    api_key = os.getenv("GEMINI_API_KEY")
    output_path = "output_structured.md"

    if api_key:
        # We have an API key! Use the AI-powered formatter
        print("[*] Step 2: Transforming layout via Gemini AI Engine...")
        try:
            # GeminiProvider is now imported cleanly from providers/__init__.py
            provider = GeminiProvider(api_key=api_key)
            markdown_output = provider.transform_text(raw_text)
            print("Gemini AI structure transformation complete!")
        except Exception as e:
            print(f"Gemini AI failed ({e}). Falling back to Local Rule Formatter...")
            formatter = MarkdownFormatter(raw_text)
            markdown_output = formatter.format_text()
    else:
        # No API key found. Use our robust local rule engine instead!
        print("[*] Step 2: Using standard local rule-based Formatter...")
        print("Tip: Save your GEMINI_API_KEY environment variable to unlock advanced AI-powered layout reconstruction!")
        formatter = MarkdownFormatter(raw_text)
        markdown_output = formatter.format_text()

    # Step 3: Save the finalized Markdown file output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_output)

    print(f"Success! Your beautifully formatted document is saved to: {output_path}")

if __name__ == "__main__":
    main()