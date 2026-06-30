# gui.py
import os
import threading
import customtkinter as ctk
from tkinter import filedialog
from core.extractor import PDFExtractor
from core.formatter import MarkdownFormatter
from providers import GeminiProvider

ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")

class PDF2MarkdownGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Settings
        self.title("PDF to Markdown AI Converter")
        
        # 1. Grab your monitor's actual resolution dimensions dynamically
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # 2. Force the window canvas to match your exact screen sizes
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # 3. Enable resizing so windows can snap it to the sides if needed later
        self.resizable(True, True)

        self.selected_pdf_path = ""
        self.converted_markdown_data = ""  # Temporary storage memory for your converted text

        # --- UI LAYOUT STRUCTURE ---
        
        # Main Grid Layout (Left Side = Controls / Right Side = Preview Screen)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # ================= LEFT CONTROL PANEL =================
        self.left_panel = ctk.CTkFrame(self, width=320)
        self.left_panel.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        self.title_label = ctk.CTkLabel(
            self.left_panel, text="⚡ PDF2Markdown AI", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.pack(padx=15, pady=20)

        # File Chooser Box
        self.file_entry = ctk.CTkEntry(self.left_panel, placeholder_text="Pick a PDF file...", width=260)
        self.file_entry.pack(padx=15, pady=5)

        self.browse_btn = ctk.CTkButton(self.left_panel, text="Browse PDF", command=self.browse_file)
        self.browse_btn.pack(padx=15, pady=5)

        # Model Dropdown Selection
        self.provider_label = ctk.CTkLabel(self.left_panel, text="Select AI Engine:", font=ctk.CTkFont(size=12, weight="bold"))
        self.provider_label.pack(padx=15, pady=(15, 0), anchor="w")
        
        self.provider_select = ctk.CTkOptionMenu(
            self.left_panel, values=["Gemini (AI Engine)", "Local Rules (Offline Fallback)"], width=260
        )
        self.provider_select.pack(padx=15, pady=5)

        # Convert Action Trigger
        self.convert_btn = ctk.CTkButton(
            self.left_panel, text="Convert Document", command=self.start_conversion_thread,
            fg_color="#1f538d", hover_color="#14375e", font=ctk.CTkFont(weight="bold")
        )
        self.convert_btn.pack(padx=15, pady=20)

        # Save Action Trigger (Initially disabled until conversion succeeds!)
        self.save_btn = ctk.CTkButton(
            self.left_panel, text="💾 Save Document As...", command=self.save_file_destination,
            fg_color="#0f391f", hover_color="#16a34a", text_color="white",
            font=ctk.CTkFont(weight="bold"), state="disabled", width=260
        )
        self.save_btn.pack(padx=15, pady=5)

        # Status System Logs
        self.log_label = ctk.CTkLabel(self.left_panel, text="System Log Trace:", font=ctk.CTkFont(size=11))
        self.log_label.pack(padx=15, pady=(15, 0), anchor="w")
        
        self.console_output = ctk.CTkTextbox(self.left_panel, width=260, height=140, font=ctk.CTkFont(family="Consolas", size=11))
        self.console_output.pack(padx=15, pady=5)

        # ================= RIGHT LIVE PREVIEW PANEL =================
        self.right_panel = ctk.CTkFrame(self)
        self.right_panel.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.right_panel.grid_rowconfigure(1, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)

        self.preview_label = ctk.CTkLabel(
            self.right_panel, text="📄 Live Markdown Output View", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.preview_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        # The interactive text area containing your converted code output
        self.viewer_output = ctk.CTkTextbox(self.right_panel, font=ctk.CTkFont(family="Consolas", size=12))
        self.viewer_output.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")

        self.log_message("System ready.")

    def log_message(self, text: str):
        self.console_output.insert("end", f"{text}\n")
        self.console_output.see("end")

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.selected_pdf_path = file_path
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, file_path)
            self.log_message(f"📂 Loaded: {os.path.basename(file_path)}")

    def start_conversion_thread(self):
        if not self.selected_pdf_path:
            self.log_message("❌ Error: Select a PDF file first.")
            return
        
        self.convert_btn.configure(state="disabled", text="Processing...")
        self.save_btn.configure(state="disabled")
        
        threading.Thread(target=self.run_pipeline, daemon=True).start()

    def run_pipeline(self):
        try:
            pdf_path = self.selected_pdf_path
            selected_engine = self.provider_select.get()

            self.log_message("\n--- Running Extraction ---")
            extractor = PDFExtractor(pdf_path)
            raw_text = extractor.extract_text()

            api_key = os.getenv("GEMINI_API_KEY")

            if "Gemini" in selected_engine and api_key:
                self.log_message("[*] Running Gemini Layout AI...")
                provider = GeminiProvider(api_key=api_key)
                self.converted_markdown_data = provider.transform_text(raw_text)
            else:
                if "Gemini" in selected_engine and not api_key:
                    self.log_message("⚠️ Key missing! Defaulting to Local Rules...")
                self.log_message("[*] Running local rule engine...")
                formatter = MarkdownFormatter(raw_text)
                self.converted_markdown_data = formatter.format_text()

            # Dynamic UI Updates: Fill the document viewer right on your display monitor
            self.viewer_output.delete("1.0", "end")
            self.viewer_output.insert("1.0", self.converted_markdown_data)
            
            self.log_message("✅ Conversion Complete!")
            
            # Instantly light up the Green save button!
            self.save_btn.configure(state="normal")

        except Exception as e:
            self.log_message(f"❌ Failure: {str(e)}")
        
        finally:
            self.convert_btn.configure(state="normal", text="Convert Document")

    def save_file_destination(self):
        """Opens a standard system directory window to save the text payload anywhere."""
        if not self.converted_markdown_data:
            return
        
        # Open a default file export dialog menu mapping to standard markdown extensions
        save_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown Document", "*.md"), ("Text File", "*.txt")],
            initialfile="converted_document.md"
        )
        
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(self.converted_markdown_data)
            self.log_message(f"🎉 Saved successfully to:\n{save_path}")

if __name__ == "__main__":
    app = PDF2MarkdownGUI()
    app.mainloop()