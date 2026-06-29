# config.py
import os

# Base directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Default output naming profiles
DEFAULT_OUTPUT_TXT = "output_raw_text.txt"
DEFAULT_OUTPUT_MD = "output_structured.md"

# Extraction Engine Configuration Profile
SETTINGS = {
    "preserve_whitespace": True,
    "encoding": "utf-8",
    "fallback_engine": "pdfplumber"
}