import os
import sys
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from dotenv import load_dotenv

from typing import Optional

class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        # .envファイルを読み込む
        load_dotenv()
        
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")
        
        if api_key is None:
            raise ValueError(
                "Gemini API key not provided directly or found in GEMINI_API_KEY environment variable. "
                "Please provide the key directly or set it in your .env file."
            )
        genai.configure(api_key=api_key)

    def generate_text(self, prompt: str) -> str:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
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

# FastAPI dependency
def get_gemini_client() -> GeminiClient:
    """
    FastAPIの依存性注入用のファクトリ関数。
    GeminiClientのインスタンスを返します。
    """
    # Use the provided API key directly
    return GeminiClient(api_key="AIzaSyA8xL_JFa-tQAZfmDlAYqhQGRtyCFP5Ch0")
