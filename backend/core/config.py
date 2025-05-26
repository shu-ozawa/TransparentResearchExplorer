import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Provider Configuration
def get_api_provider() -> str:
    """
    Determines the API provider based on the API_PROVIDER environment variable.

    Returns:
        str: "ollama" if API_PROVIDER is set to "ollama" (case-insensitive).
             Otherwise, defaults to "gemini".
    """
    api_provider = os.getenv("API_PROVIDER")
    if api_provider and api_provider.lower() == "ollama":
        return "ollama"
    return "gemini"

# API Keys and Base URLs (can be imported by respective clients)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "ollama")

if __name__ == '__main__':
    # Example usage and testing
    print(f"GEMINI_API_KEY: {GEMINI_API_KEY}") # Might be None if not set
    print(f"OLLAMA_BASE_URL: {OLLAMA_BASE_URL}")
    print(f"OLLAMA_API_KEY: {OLLAMA_API_KEY}")

    # Test get_api_provider
    # To test, you would run this script with API_PROVIDER set in your environment
    # For example: API_PROVIDER=ollama python backend/core/config.py
    print(f"Current API Provider: {get_api_provider()}")

    # Test with a specific value (simulating environment variable)
    os.environ["API_PROVIDER"] = "OLLAMA"
    print(f"API Provider (set to OLLAMA): {get_api_provider()}")

    os.environ["API_PROVIDER"] = "gemini"
    print(f"API Provider (set to gemini): {get_api_provider()}")

    os.environ["API_PROVIDER"] = "some_other_value"
    print(f"API Provider (set to some_other_value): {get_api_provider()}")

    del os.environ["API_PROVIDER"] # Unset for next test
    print(f"API Provider (unset): {get_api_provider()}")
