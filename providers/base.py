import time
from abc import ABC, abstractmethod

class BaseProvider(ABC):
    """Abstract Base Class enforcing a uniform API interface with built-in resilient backoff."""
    
    def __init__(self, api_key: str, model_name: str):
        if not api_key:
            raise ValueError(f"Initialization Failed: API Key for {self.__class__.__name__} is missing.")
        self.api_key = api_key
        self.model_name = model_name

    @abstractmethod
    def _execute_request(self, system_prompt: str, user_prompt: str) -> str:
        """Low-level execution implementation unique to each AI SDK wrapper layer."""
        pass

    def transform_text(self, raw_text: str, chunk_index: int = None) -> str:
        """
        Unified public execution wrapper. Coordinates system instructions, 
        cleans text streams, and implements standardized exponential backoff for rate limits.
        """
        if not raw_text.strip():
            return ""

        system_prompt = (
            "You are an expert document structural layout engineer.\n"
            "Convert the raw PDF text block into clean, professional Markdown.\n"
            "Requirements:\n"
            "1. Maintain all original hierarchy (headers, sub-headers, lists, tables).\n"
            "2. Fix broken words or hyphenations caused by PDF page clipping boundary errors.\n"
            "3. Output ONLY the raw markdown code. Do NOT add conversational preambles or chat notes."
        )

        max_retries = 5
        backoff_factor = 2

        for attempt in range(max_retries):
            try:
                return self._execute_request(system_prompt, raw_text)
            except Exception as e:
                err_msg = str(e).lower()
                # Intercept common rate limits: HTTP 429, ResourceExhausted, Overloaded
                if "429" in err_msg or "exhausted" in err_msg or "overloaded" in err_msg:
                    sleep_time = backoff_factor ** attempt
                    time.sleep(sleep_time)
                    continue
                else:
                    raise RuntimeError(f"Engine Exception on chunk {chunk_index}: {str(e)}")
                    
        raise TimeoutError(f"Failed to process chunk {chunk_index} after {max_retries} retries due to rate restrictions.")