# cli.py
import os
import argparse
import sys
from dotenv import load_dotenv

# Ensure configuration files are loaded natively before imports run
load_dotenv()

from core.chunker import DocumentChunker
from core.extractor import PDFExtractor
from core.formatter import MarkdownFormatter
from providers import GeminiProvider, OpenAIProvider, AnthropicProvider

def main():
    parser = argparse.ArgumentParser(
        description="PDF2Markdown Heavy-Duty CLI (Enterprise Large-Scale Translation Engine)"
    )
    
    # Core operational command arguments
    parser.add_argument("pdf_path", type=str, help="Absolute or relative path location to target PDF file.")
    parser.add_argument("-o", "--output", type=str, default="output.md", help="Destination path for compiled Markdown text. (Default: output.md)")
    parser.add_argument("-e", "--engine", type=str, choices=["gemini", "chatgpt", "claude", "local"], default="gemini",
                        help="AI translation engine selection or local rule fallback loop. (Default: gemini)")
    parser.add_argument("-c", "--chunk-size", type=int, default=5, help="Number of canvas pages to group into an independent packet. (Default: 5)")
    parser.add_argument("-r", "--range", type=str, default=None, 
                        help="Target page range subset selection boundary (e.g., '1-10' or '5-12'). Processes full document if omitted.")

    args = parser.parse_args()

    print("\n========================================================")
    print("PDF2Markdown Enterprise CLI Deployment Layer Running")
    print("========================================================")

    # Validate target file exists safely via our standard extractor guard rails
    if not os.path.exists(args.pdf_path):
        print(f"Critical Execution Error: Target file missing at '{args.pdf_path}'")
        sys.exit(1)

    try:
        # 1. Parse Document Architecture Boundaries
        print("[*] Analyzing document structural segments...")
        chunker = DocumentChunker(args.pdf_path)
        raw_chunks = chunker.generate_chunks(pages_per_chunk=args.chunk_size)
        
        # 2. Filter via Page Range Flag Constraints if Supplied
        chunks = []
        if args.range:
            try:
                start_range, end_range = map(int, args.range.split("-"))
                print(f"Target Page Filtering Active: Processing isolated range {start_range} to {end_range}")
                
                for chunk in raw_chunks:
                    # Match chunks that overlap or fall within the requested page range boundaries
                    if chunk["start_p"] <= end_range and chunk["end_p"] >= start_range:
                        chunks.append(chunk)
            except Exception:
                print("Operational Parameter Error: Range flag formatting must exactly mirror syntax 'start-end' (e.g., -r 1-10).")
                sys.exit(1)
        else:
            chunks = raw_chunks

        if not chunks:
            print("Filtering Constraint Anomaly: No page packets match the defined range parameters.")
            sys.exit(0)

        total_chunks = len(chunks)
        print(f"Active Processing Pipeline initialized with {total_chunks} chunk packets.")
        compiled_results = [""] * total_chunks

        # 3. Dynamic Unified Provider Routing
        provider = None
        if args.engine == "gemini":
            key = os.getenv("GEMINI_API_KEY")
            print("[*] Initializing Uniform Google Gemini Core...")
            provider = GeminiProvider(api_key=key)
        elif args.engine == "chatgpt":
            key = os.getenv("OPENAI_API_KEY")
            print("[*] Initializing Uniform OpenAI ChatGPT Core...")
            provider = OpenAIProvider(api_key=key)
        elif args.engine == "claude":
            key = os.getenv("ANTHROPIC_API_KEY")
            print("[*] Initializing Uniform Anthropic Claude Core...")
            provider = AnthropicProvider(api_key=key)
        else:
            print("[*] Selected Local Rules Engine. Bypassing cloud API provider routes entirely...")

        # 4. Multi-Threaded Concurrent Execution Pipeline
        if provider is not None:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            MAX_THREADS = 3
            print(f"[*] Dispatching concurrent thread pool loops across {MAX_THREADS} parallel workers...")
            
            with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                # We track the relative working position using dictionary enumerations to guarantee sequence order alignment
                future_to_chunk_index = {
                    executor.submit(provider.transform_text, chunk["text"], chunk["index"]): i 
                    for i, chunk in enumerate(chunks)
                }
                
                completed_count = 0
                for future in as_completed(future_to_chunk_index):
                    list_position = future_to_chunk_index[future]
                    chunk_meta = chunks[list_position]
                    try:
                        markdown_data = future.result()
                        compiled_results[list_position] = markdown_data
                        completed_count += 1
                        percentage = int((completed_count / total_chunks) * 100)
                        print(f"Chunks Complete: {completed_count}/{total_chunks} [{percentage}%] | Processed Pages {chunk_meta['start_p']}-{chunk_meta['end_p']}")
                    except Exception as e:
                        # Automated Local Exception Fallback Loop Execution Path
                        print(f"AI Error encountered on Pages {chunk_meta['start_p']}-{chunk_meta['end_p']}: {str(e)}")
                        print(f"Executing Local Rule Fallback for Pages {chunk_meta['start_p']}-{chunk_meta['end_p']}...")
                        formatter = MarkdownFormatter(chunk_meta["text"])
                        compiled_results[list_position] = formatter.format_text()

            final_markdown_data = "\n\n".join(compiled_results)
        else:
            # Full Local Offline Rule Processing Route
            print("[*] Executing local unified layout rules parser across targets...")
            extractor = PDFExtractor(args.pdf_path)
            # If a range was selected, compile only the text from the matching chunks
            if args.range:
                full_raw_text = "\n\n".join([c["text"] for c in chunks])
            else:
                full_raw_text = extractor.extract_text()
                
            formatter = MarkdownFormatter(full_raw_text)
            final_markdown_data = formatter.format_text()

        # 5. File Serialization Stream Layer
        print(f"[*] Writing compiled file assets to target disk path at '{args.output}'...")
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(final_markdown_data)
            
        print("\nEnterprise Document Conversion Sequence Successful!\n")

    except Exception as e:
        print(f"\nCritical CLI Execution Failure: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()