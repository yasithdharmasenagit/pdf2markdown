# providers/gemini.py
import time
import google.generativeai as genai

class GeminiProvider:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API Key missing.")
        genai.configure(api_key=api_key)
        # Using 2.5-flash as it has a massive context window and rapid processing speeds
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def transform_text(self, raw_text: str, chunk_index: int = None) -> str:
        """Sends a specific text block to Gemini with robust error handling and retries."""
        if not raw_text.strip():
            return ""

        # System instructions engineered specifically to keep markdown clean across stitched chunks
        prompt = (
            "You are an expert document structural layout engineer.\n"
            "Your task is to convert the following raw PDF extracted text into clean, professional Markdown.\n"
            "Requirements:\n"
            "1. Maintain all original hierarchy (headers, sub-headers, lists, bullet points).\n"
            "2. Fix broken words or hyphenations caused by PDF page clipping.\n"
            "3. Do NOT add any conversational introduction or conclusion text. Output ONLY the raw markdown code.\n"
            "4. Preserve formatting blocks, code sections, or tables cleanly.\n\n"
            f"--- RAW TEXT BLOCK ---\n{raw_text}"
        )

        max_retries = 5
        backoff_factor = 2

        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                if response.text:
                    return response.text
                raise Exception("Empty response received from Gemini infrastructure.")
            
            except Exception as e:
                # If we get rate limited (HTTP 429) due to many pages hitting the API, back off gracefully
                if "429" in str(e) or "ResourceExhausted" in str(e):
                    sleep_time = backoff_factor ** attempt
                    time.sleep(sleep_time)
                    continue
                else:
                    raise e
                    
        raise Exception(f"Failed to process chunk {chunk_index} after multiple safe retrying attempts.")