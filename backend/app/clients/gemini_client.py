import sys
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from typing import Optional

class GeminiClient:
    def __init__(self, api_key: str):
        """
        Initializes the GeminiClient.
        Requires an API key to be passed directly.
        """
        if not api_key:
            # This check is a safeguard, but the factory in dependencies.py
            # should ensure a valid key is passed.
            raise ValueError("Gemini API key must be provided.")
        genai.configure(api_key=api_key)

    def generate_text(self, prompt: str, model: Optional[str] = None) -> str:
        default_model_name = 'gemini-2.5-flash-preview-05-20'
        effective_model_name = model if model else default_model_name

        generative_model = genai.GenerativeModel(effective_model_name)
        try:
            response = generative_model.generate_content(prompt)
            # Ensure response.text is accessible and not None
            if hasattr(response, 'text') and response.text:
                return response.text
            else:
                # Check parts if text is not directly available
                if hasattr(response, 'parts') and response.parts:
                    return "".join(part.text for part in response.parts if hasattr(part, 'text') and part.text)
                print("Gemini API Error: Empty response or text unavailable.", file=sys.stderr)
                return ""
        except google_exceptions.GoogleAPIError as e:
            print(f"Gemini API Error: {e}", file=sys.stderr)
            return ""
        except Exception as e:
            print(f"An unexpected error occurred: {e}", file=sys.stderr)
            return ""
