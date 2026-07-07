# gui.py
import os
import threading
import customtkinter as ctk
from tkinter import filedialog
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.extractor import PDFExtractor
from core.formatter import MarkdownFormatter
from providers import GeminiProvider, OpenAIProvider, AnthropicProvider
from dotenv import load_dotenv
load_dotenv()

ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")

class PDF2MarkdownGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PDF to Markdown AI Converter (Enterprise Large-Scale Edition)")
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        self.resizable(True, True)

        self.selected_pdf_path = ""
        self.converted_markdown_data = ""

        # --- UI GRID STRUCTURE ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # ================= LEFT SIDEBAR (CONTROLS) =================
        self.left_panel = ctk.CTkFrame(self, width=320)
        self.left_panel.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        self.title_label = ctk.CTkLabel(self.left_panel, text="PDF2Markdown Heavy-Duty", font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.pack(padx=15, pady=20)

        self.file_entry = ctk.CTkEntry(self.left_panel, placeholder_text="Pick a PDF file...", width=260)
        self.file_entry.pack(padx=15, pady=5)

        self.browse_btn = ctk.CTkButton(self.left_panel, text="Browse PDF", command=self.browse_file)
        self.browse_btn.pack(padx=15, pady=5)

        self.provider_label = ctk.CTkLabel(self.left_panel, text="Select AI Engine:", font=ctk.CTkFont(size=12, weight="bold"))
        self.provider_label.pack(padx=15, pady=(15, 0), anchor="w")
        
        self.provider_select = ctk.CTkOptionMenu(self.left_panel, values=["Gemini (AI Parallel Chunks Engine)", "ChatGPT (OpenAI Core)", "Claude (Anthropic Engine)", "Local Rules (Offline Local Fallback)"], width=260)
        self.provider_select.pack(padx=15, pady=5)

        self.convert_btn = ctk.CTkButton(self.left_panel, text="Convert Document", command=self.start_conversion_thread, fg_color="#1f538d", hover_color="#14375e", font=ctk.CTkFont(weight="bold"))
        self.convert_btn.pack(padx=15, pady=20)

        self.save_btn = ctk.CTkButton(self.left_panel, text="Save Document As...", command=self.save_file_destination, fg_color="#1b6335", hover_color="#16a34a", text_color="white", font=ctk.CTkFont(weight="bold"), state="disabled", width=260)
        self.save_btn.pack(padx=15, pady=5)

        self.log_label = ctk.CTkLabel(self.left_panel, text="System Log Trace:", font=ctk.CTkFont(size=11))
        self.log_label.pack(padx=15, pady=(15, 0), anchor="w")
        
        self.console_output = ctk.CTkTextbox(self.left_panel, width=260, height=250, font=ctk.CTkFont(family="Consolas", size=11))
        self.console_output.pack(padx=15, pady=5)

        # ================= RIGHT CANVAS (PREVIEW SCREEN) =================
        self.right_panel = ctk.CTkFrame(self)
        self.right_panel.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.right_panel.grid_rowconfigure(1, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)

        self.preview_label = ctk.CTkLabel(self.right_panel, text="Live Compiled Markdown Output View", font=ctk.CTkFont(size=14, weight="bold"))
        self.preview_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.viewer_output = ctk.CTkTextbox(self.right_panel, font=ctk.CTkFont(family="Consolas", size=12))
        self.viewer_output.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")

        self.log_message("System processing layer initialized.")

    def log_message(self, text: str):
        self.console_output.insert("end", f"{text}\n")
        self.console_output.see("end")

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.selected_pdf_path = file_path
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, file_path)
            self.log_message(f"Loaded: {os.path.basename(file_path)}")

    def start_conversion_thread(self):
        if not self.selected_pdf_path:
            self.log_message("Error: Select a PDF file first.")
            return
        
        self.convert_btn.configure(state="disabled", text="Processing Work...")
        self.save_btn.configure(state="disabled")
        self.viewer_output.delete("1.0", "end")
        
        threading.Thread(target=self.run_pipeline, daemon=True).start()

    def run_pipeline(self):
        """Advanced execution pipeline layer parsing token estimates, checkpoints, and layouts."""
        pdf_path = self.file_entry.get().strip()
        raw_provider_value = self.provider_select.get()
        engine_selection = raw_provider_value.split()[0].lower()
        output_markdown_path = "gui_output.md" 

        if not pdf_path or not os.path.exists(pdf_path):
            self.log_message("Critical Error: Target file path selection is missing or invalid.")
            self._reset_ui_buttons()
            return

        try:
            self.log_message("========================================================")
            self.log_message("PDF2Markdown Professional UI Pipeline Active")
            self.log_message("========================================================")

            # 1. Structural Chunk Generation Pass
            from core.chunker import DocumentChunker
            chunker = DocumentChunker(pdf_path, use_ocr=False)
            chunks = chunker.generate_chunks(pages_per_chunk=5)
            total_chunks = len(chunks)

            # 2. Phase 4 Cost & Token Calculation Estimation
            from core.analytics import RuntimeExecutionSuite
            metrics = RuntimeExecutionSuite.estimate_token_costs(chunks, engine_selection)
            self.log_message(f"Volume Metrics: ~{metrics['tokens']:,} Tokens | Estimated Run Cost: ${metrics['cost']:.4f}")

            # 3. Phase 4 Session Cache Recovery Checkpoints
            saved_progress = RuntimeExecutionSuite.load_progress(output_markdown_path)
            if saved_progress:
                self.log_message(f"Checkpoint Cache Found! Automatically recovering {len(saved_progress)} segments.")

            compiled_results = [""] * total_chunks
            
            # Rehydrate completed chunk positions from local save state
            for idx in range(total_chunks):
                if str(idx) in saved_progress:
                    compiled_results[idx] = saved_progress[str(idx)]

            # 4. Resolve Dynamic Provider Instances
            provider = self._get_active_provider(engine_selection)

            # 5. Multi-Threaded Process Framework Mapping Loop
            if provider is not None:
                from concurrent.futures import ThreadPoolExecutor, as_completed
                
                # Identify remaining items to minimize duplicate API charges
                unprocessed_indices = [i for i in range(total_chunks) if str(chunks[i]["index"]) not in saved_progress]

                if unprocessed_indices:
                    self.log_message(f"[*] Dispatching concurrent background threads for {len(unprocessed_indices)} chunks...")
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
                                
                                # Instantly checkpoint state block on disk
                                RuntimeExecutionSuite.save_progress(output_markdown_path, chunk_meta["index"], markdown_chunk)
                                self.log_message(f"Packets Resolved: Chunk {chunk_meta['index']} | Pages {chunk_meta['start_p']}-{chunk_meta['end_p']}")
                            except Exception as e:
                                self.log_message(f"AI Error on pages {chunk_meta['start_p']}: Running local layout fallback rule...")
                                from core.formatter import MarkdownFormatter
                                formatter = MarkdownFormatter(chunk_meta["structured_data"])
                                fallback_md = formatter.format_text()
                                compiled_results[pos] = fallback_md
                                RuntimeExecutionSuite.save_progress(output_markdown_path, chunk_meta["index"], fallback_md)

                final_body_text = "\n\n".join(compiled_results)
            else:
                # Local Rules Fallback Route
                self.log_message("[*] Running local layout rules parsing engine...")
                from core.formatter import MarkdownFormatter
                formatter = MarkdownFormatter(chunker.generate_chunks(10000)[0]["structured_data"])
                final_body_text = formatter.format_text()

            # 6. Extract structural YAML Frontmatter & Bookmarks Outlines
            from core.metadata import DocumentMetadataParser
            meta_engine = DocumentMetadataParser(pdf_path)
            frontmatter = meta_engine.generate_frontmatter_and_toc()

            # 7. Final Output Aggregation File Stream Assembly
            self.converted_markdown_data = frontmatter + "\n\n" + final_body_text
            
            with open(output_markdown_path, "w", encoding="utf-8") as f:
                f.write(self.converted_markdown_data)

            # Clear temporary json checkpoints on a successful run completion
            RuntimeExecutionSuite.clear_progress(output_markdown_path)
            
            # 🎯 FIXED: Direct text insertion into our read-only text viewer widget canvas
            self.viewer_output.insert("1.0", self.converted_markdown_data)
            self.log_message("\nGUI Document Conversion Sequence Successful!\n")

        except Exception as e:
            self.log_message(f"\nCritical Pipeline Error: {str(e)}\n")
        
        finally:
            # Re-activate operational trigger fields for the operator interface
            self._reset_ui_buttons()

    def _reset_ui_buttons(self):
        """Restores CTA button interaction state capabilities back onto the user interface canvas."""
        self.convert_btn.configure(state="normal", text="Convert Document")
        if self.converted_markdown_data:
            self.save_btn.configure(state="normal")

    def _get_active_provider(self, engine_name: str):
        """Matches selected interface keys with matching unified backend provider structures."""
        from providers import GeminiProvider, OpenAIProvider, AnthropicProvider
        
        if engine_name == "gemini":
            return GeminiProvider(api_key=os.getenv("GEMINI_API_KEY"))
        elif engine_name == "chatgpt":
            return OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
        elif engine_name == "claude":
            return AnthropicProvider(api_key=os.getenv("ANTHROPIC_API_KEY"))
        return None 
    
    def save_file_destination(self):
        if not self.converted_markdown_data:
            return
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown Document", "*.md"), ("Text File", "*.txt")],
            initialfile="large_converted_document.md"
        )
        
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(self.converted_markdown_data)
            self.log_message(f"Saved successfully to:\n{save_path}")

if __name__ == "__main__":
    app = PDF2MarkdownGUI()
    app.mainloop()