# cli.py
import os
import argparse
import sys
from dotenv import load_dotenv

load_dotenv()

from core.chunker import DocumentChunker
from core.extractor import PDFExtractor
from core.formatter import MarkdownFormatter
from core.metadata import DocumentMetadataParser
from core.analytics import RuntimeExecutionSuite
from providers import GeminiProvider, OpenAIProvider, AnthropicProvider

def main():
    parser = argparse.ArgumentParser(description="⚡ PDF2Markdown Enterprise CLI Engine")
    parser.add_argument("pdf_path", type=str, help="Path location to target PDF file.")
    parser.add_argument("-o", "--output", type=str, default="output.md", help="Destination path. (Default: output.md)")
    parser.add_argument("-e", "--engine", type=str, choices=["gemini", "chatgpt", "claude", "local"], default="gemini")
    parser.add_argument("-c", "--chunk-size", type=int, default=5, help="Pages per chunk package.")
    parser.add_argument("-r", "--range", type=str, default=None, help="Target range subset '1-10'.")
    parser.add_argument("--ocr", action="store_true", help="Enable optical character recognition fallback.")
    parser.add_argument("-y", "--yes", action="store_true", help="Auto-approve spend predictions and skip safety prompts.")

    args = parser.parse_args()

    print("\n========================================================")
    print("PDF2Markdown Professional CLI Operational Workspace")
    print("========================================================")

    if not os.path.exists(args.pdf_path):
        print(f"Critical Error: Target file missing at '{args.pdf_path}'")
        sys.exit(1)

    try:
        # 1. Parse Data Architecture Boundaries
        chunker = DocumentChunker(args.pdf_path, use_ocr=args.ocr)
        chunks = chunker.generate_chunks(pages_per_chunk=args.chunk_size)
        
        # 2. Estimate Financial Resource Use Fields
        metrics = RuntimeExecutionSuite.estimate_token_costs(chunks, args.engine)
        print(f"Pipeline Cost Metrics: Volume ~{metrics['tokens']:,} tokens | Expected Cost: ${metrics['cost']:.4f}")
        
        if not args.yes and metrics['cost'] > 0.05 and args.engine != "local":
            confirm = input("Spend Threshold Confirmation Alert! Approve API processing? (y/N): ")
            if confirm.lower() != 'y':
                print("Processing safely aborted by developer input choices.")
                sys.exit(0)

        # 3. Read Session Cache Recovery States
        saved_progress = RuntimeExecutionSuite.load_progress(args.output)
        if saved_progress:
            print(f"Checkpoint Cache Recovered! Found {len(saved_progress)} completed data segments.")

        compiled_results = [""] * len(chunks)
        provider = None
        
        if args.engine == "gemini":
            provider = GeminiProvider(api_key=os.getenv("GEMINI_API_KEY"))
        elif args.engine == "chatgpt":
            provider = OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
        elif args.engine == "claude":
            provider = AnthropicProvider(api_key=os.getenv("ANTHROPIC_API_KEY"))

        # 4. Multi-Threaded Process Framework Mapping Loop
        if provider is not None:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            # Identify missing chunks that still need processing
            unprocessed_indices = [i for i in range(len(chunks)) if str(chunks[i]["index"]) not in saved_progress]
            
            # Fill compiled array layout slots with recovered values
            for idx in range(len(chunks)):
                if str(idx) in saved_progress:
                    compiled_results[idx] = saved_progress[str(idx)]

            if unprocessed_indices:
                print(f"[*] Dispatching thread workers to resolve {len(unprocessed_indices)} remaining chunk packets...")
                with ThreadPoolExecutor(max_workers=3) as executor:
                    future_to_index = {
                        executor.submit(provider.transform_text, chunks[i]["text"], chunks[i]["index"]): i 
                        for i in unprocessed_indices
                    }
                    
                    for future in as_completed(future_to_index):
                        pos = future_to_index[future]
                        chunk_meta = chunks[pos]
                        try:
                            markdown_chunk = future.result()
                            compiled_results[pos] = markdown_chunk
                            # Instantly save progress to prevent loss on network dropout
                            RuntimeExecutionSuite.save_progress(args.output, chunk_meta["index"], markdown_chunk)
                            print(f"Packets Resolved: Index {chunk_meta['index']} | Pages {chunk_meta['start_p']}-{chunk_meta['end_p']}")
                        except Exception as e:
                            print(f"Local Fallback triggered on page segments {chunk_meta['start_p']}: {str(e)}")
                            formatter = MarkdownFormatter(chunk_meta["structured_data"])
                            fallback_md = formatter.format_text()
                            compiled_results[pos] = fallback_md
                            RuntimeExecutionSuite.save_progress(args.output, chunk_meta["index"], fallback_md)

            final_body_text = "\n\n".join(compiled_results)
        else:
            print("[*] Running local offline structural rules parsing engine...")
            formatter = MarkdownFormatter(chunker.generate_chunks(10000)[0]["structured_data"])
            final_body_text = formatter.format_text()

        # 5. Extract structural YAML Frontmatter & Bookmarks Outlines
        meta_engine = DocumentMetadataParser(args.pdf_path)
        frontmatter = meta_engine.generate_frontmatter_and_toc()

        # 6. Final File Compilation Assembly
        print(f"[*] Writing complete asset outputs to file disk path at '{args.output}'...")
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(frontmatter + "\n\n" + final_body_text)
            
        # Clean up recovery files on success
        RuntimeExecutionSuite.clear_progress(args.output)
        print("\nEnterprise Document Conversion Sequence Successful!\n")

    except Exception as e:
        print(f"\nCritical CLI Run Error: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()