import os
import sys
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key is None:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        genai.configure(api_key=api_key)

    def generate_text(self, prompt: str) -> str:
        model = genai.GenerativeModel('gemini-pro')
        try:
            response = model.generate_content(prompt)
            # Ensure response.text is accessible and not None
            if response.text:
                return response.text
            else:
                # Check parts if text is not directly available
                if response.parts:
                    return "".join(part.text for part in response.parts if hasattr(part, 'text'))
                print("Gemini API Error: Empty response or text unavailable.", file=sys.stderr)
                return ""
        except google_exceptions.GoogleAPIError as e:
            print(f"Gemini API Error: {e}", file=sys.stderr)
            return ""
        except Exception as e:
            print(f"An unexpected error occurred: {e}", file=sys.stderr)
            return ""
