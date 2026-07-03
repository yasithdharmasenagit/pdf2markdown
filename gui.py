# gui.py
import os
import threading
import customtkinter as ctk
from tkinter import filedialog
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.extractor import PDFExtractor
from core.formatter import MarkdownFormatter
from providers import GeminiProvider, OpenAIProvider, AnthropicProvider

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
        
        self.title_label = ctk.CTkLabel(self.left_panel, text="⚡ PDF2Markdown Heavy-Duty", font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.pack(padx=15, pady=20)

        self.file_entry = ctk.CTkEntry(self.left_panel, placeholder_text="Pick a PDF file...", width=260)
        self.file_entry.pack(padx=15, pady=5)

        self.browse_btn = ctk.CTkButton(self.left_panel, text="Browse PDF", command=self.browse_file)
        self.browse_btn.pack(padx=15, pady=5)

        self.provider_label = ctk.CTkLabel(self.left_panel, text="Select AI Engine:", font=ctk.CTkFont(size=12, weight="bold"))
        self.provider_label.pack(padx=15, pady=(15, 0), anchor="w")
        
        self.provider_select = ctk.CTkOptionMenu(
            self.left_panel, values=["Gemini (AI Parallel Chunks Engine)", "ChatGPT (OpenAI Core)", "Claude (Anthropic Engine)", "Local Rules (Offline Local Fallback)"], width=260
        )
        self.provider_select.pack(padx=15, pady=5)

        self.convert_btn = ctk.CTkButton(
            self.left_panel, text="Convert Document", command=self.start_conversion_thread,
            fg_color="#1f538d", hover_color="#14375e", font=ctk.CTkFont(weight="bold")
        )
        self.convert_btn.pack(padx=15, pady=20)

        self.save_btn = ctk.CTkButton(
            self.left_panel, text="Save Document As...", command=self.save_file_destination,
            fg_color="#1b6335", hover_color="#16a34a", text_color="white",
            font=ctk.CTkFont(weight="bold"), state="disabled", width=260
        )
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
        try:
            pdf_path = self.selected_pdf_path
            selected_engine = self.provider_select.get()

            self.log_message("\n--- Running Large Document Pipeline ---")
            self.log_message("[*] Initializing decoupled chunk parsing core...")
            
            # Use our unified, shared chunker module!
            from core.chunker import DocumentChunker
            chunker = DocumentChunker(pdf_path)
            chunks = chunker.generate_chunks(pages_per_chunk=5)
            total_chunks = len(chunks)
            
            self.log_message(f"📦 Successfully parsed file matrix into {total_chunks} chunk packets.")
            compiled_results = [""] * total_chunks

            # --- DYNAMIC MULTI-AI ENGINE ROUTER ---
            provider = None
            
            if "Gemini" in selected_engine:
                gemini_key = os.getenv("GEMINI_API_KEY")
                self.log_message("[*] Initializing Uniform Google Gemini Core...")
                provider = GeminiProvider(api_key=gemini_key)
                
            elif "ChatGPT" in selected_engine:
                openai_key = os.getenv("OPENAI_API_KEY")
                self.log_message("[*] Initializing Uniform OpenAI ChatGPT Core...")
                provider = OpenAIProvider(api_key=openai_key)
                
            elif "Claude" in selected_engine:
                anthropic_key = os.getenv("ANTHROPIC_API_KEY")
                self.log_message("[*] Initializing Uniform Anthropic Claude Core...")
                provider = AnthropicProvider(api_key=anthropic_key)

            # --- EXECUTION PIPELINE LAYER ---
            if provider is not None:
                self.log_message("[*] Launching Concurrent Thread Worker Pools...")
                MAX_THREADS = 3 
                
                with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                    future_to_chunk = {
                        executor.submit(provider.transform_text, chunk["text"], chunk["index"]): chunk 
                        for chunk in chunks
                    }
                    
                    completed_count = 0
                    for future in as_completed(future_to_chunk):
                        chunk_meta = future_to_chunk[future]
                        try:
                            markdown_chunk_data = future.result()
                            compiled_results[chunk_meta["index"]] = markdown_chunk_data
                            
                            completed_count += 1
                            percentage = int((completed_count / total_chunks) * 100)
                            self.log_message(
                                f"➡️ Chunks Complete: {completed_count}/{total_chunks} "
                                f"[{percentage}%] | Processed Pages {chunk_meta['start_p']}-{chunk_meta['end_p']}"
                            )
                        except Exception as e:
                            # Safe localized fallback logic
                            self.log_message(f"❌ AI Error on chunk {chunk_meta['index']}: {str(e)}")
                            self.log_message(f"🔄 Executing Local Rule Fallback for Pages {chunk_meta['start_p']}-{chunk_meta['end_p']}...")
                            
                            formatter = MarkdownFormatter(chunk_meta["text"])
                            compiled_results[chunk_meta["index"]] = formatter.format_text()

                self.converted_markdown_data = "\n\n".join(compiled_results)
            
            else:
                self.log_message("[*] Executing local offline structural rules...")
                extractor = PDFExtractor(pdf_path)
                full_raw_text = extractor.extract_text()
                formatter = MarkdownFormatter(full_raw_text)
                self.converted_markdown_data = formatter.format_text()

            self.viewer_output.delete("1.0", "end")
            self.viewer_output.insert("1.0", self.converted_markdown_data)
            self.log_message("\n🎉 Document Conversion Sequence Successful!")
            self.save_btn.configure(state="normal")

        except Exception as e:
            self.log_message(f"❌ Critical Pipeline Failure: {str(e)}")
        
        finally:
            self.convert_btn.configure(state="normal", text="Convert Document")

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