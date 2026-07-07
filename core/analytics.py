# core/analytics.py
import os
import json

class RuntimeExecutionSuite:
    """Manages structural API cost metrics and coordinates background processing save states."""
    
    # 2026 Developer Token Reference Matrix Rates per Million Input Tokens
    PRICING = {
        "gemini": {"input": 0.075, "output": 0.30},
        "chatgpt": {"input": 2.50, "output": 10.00},
        "claude": {"input": 0.25, "output": 1.25}
    }

    @staticmethod
    def estimate_token_costs(chunks: list, engine: str) -> dict:
        """Provides token counts and estimated operational costs based on raw text chunk sizes."""
        total_chars = 0
        
        for chunk in chunks:
            # Safely read raw text payloads out of our generated chunk mapping structures
            text_payload = chunk.get("text", "")
            total_chars += len(text_payload)
            
        # Standard rough heuristic calculation: ~4 characters equals roughly 1 model token
        estimated_tokens = int(total_chars / 4)
        
        rates = RuntimeExecutionSuite.PRICING.get(engine.lower(), {"input": 0, "output": 0})
        cost = (estimated_tokens / 1000000) * rates["input"]
        
        return {
            "tokens": estimated_tokens,
            "cost": round(cost, 4)
        }

    @staticmethod
    def load_progress(output_path: str) -> dict:
        """Retrieves checkpoint cache markers from disk to continue an interrupted run."""
        progress_file = f"{output_path}.progress.json"
        if os.path.exists(progress_file):
            try:
                with open(progress_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    @staticmethod
    def save_progress(output_path: str, chunk_index: int, output_text: str):
        """Saves completed chunk transformations into a local state recovery file."""
        progress_file = f"{output_path}.progress.json"
        state = {}
        if os.path.exists(progress_file):
            try:
                with open(progress_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
            except Exception:
                pass
        
        state[str(chunk_index)] = output_text
        with open(progress_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    @staticmethod
    def clear_progress(output_path: str):
        """Cleans up checkpoint state caches once a document compiles successfully."""
        progress_file = f"{output_path}.progress.json"
        if os.path.exists(progress_file):
            try:
                os.remove(progress_file)
            except Exception:
                pass