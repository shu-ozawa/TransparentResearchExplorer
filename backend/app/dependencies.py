import os
from typing import Union, TypeVar

from backend.app.clients.gemini_client import GeminiClient
from backend.app.clients.ollama_client import OllamaClient
from backend.core.config import get_api_provider, GEMINI_API_KEY, OLLAMA_BASE_URL, OLLAMA_API_KEY

# For type hinting, we can define a type that represents either client.
# A Protocol could be used for stricter interface checking, but Union is simpler for now.
LLMClient = Union[GeminiClient, OllamaClient]
# Alternatively, using a TypeVar if we were to define a common base class or protocol later:
# LLMClientType = TypeVar("LLMClientType", bound="BaseLLMClient")


def get_llm_client() -> LLMClient:
    """
    Factory function to get an instance of an LLM client based on the API_PROVIDER setting.

    Reads the API_PROVIDER from environment variables via `get_api_provider()`.
    Initializes and returns either a GeminiClient or an OllamaClient configured
    with settings from `backend.core.config`.

    Raises:
        ValueError: If the API_PROVIDER is "gemini" and GEMINI_API_KEY is not set.
        ValueError: If the API_PROVIDER is unknown (though `get_api_provider` has a default).

    Returns:
        LLMClient: An instance of GeminiClient or OllamaClient.
    """
    provider = get_api_provider()

    if provider == "gemini":
        if not GEMINI_API_KEY:
            raise ValueError(
                "API_PROVIDER is set to 'gemini', but GEMINI_API_KEY is not configured. "
                "Please set the GEMINI_API_KEY environment variable."
            )
        return GeminiClient(api_key=GEMINI_API_KEY)
    elif provider == "ollama":
        # OLLAMA_BASE_URL and OLLAMA_API_KEY have defaults in config.py,
        # so no explicit check for None is needed here unless we want to override that.
        return OllamaClient(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)
    else:
        # This case should ideally not be reached if get_api_provider() has a default.
        raise ValueError(f"Unknown API_PROVIDER: {provider}. Supported values are 'gemini' or 'ollama'.")

if __name__ == '__main__':
    # Example of how to use the factory.
    # This requires environment variables to be set appropriately.
    # For example, to test Gemini:
    # export API_PROVIDER=gemini
    # export GEMINI_API_KEY="your_gemini_api_key"
    # python backend/app/dependencies.py

    # To test Ollama:
    # export API_PROVIDER=ollama
    # (OLLAMA_BASE_URL and OLLAMA_API_KEY will use defaults if not set)
    # python backend/app/dependencies.py

    print(f"Attempting to get LLM client based on API_PROVIDER='{os.getenv('API_PROVIDER')}'...")
    try:
        client = get_llm_client()
        print(f"Successfully obtained client of type: {type(client)}")
        if isinstance(client, GeminiClient):
            print("Gemini client configured.")
            # Note: Actual API call is not made here to avoid external dependencies in this test.
        elif isinstance(client, OllamaClient):
            print("Ollama client configured.")
            print(f"  Base URL: {client.client.base_url}")
            # Note: Actual API call is not made here.
    except ValueError as e:
        print(f"Error getting LLM client: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # Test specific scenarios
    print("\nTesting Gemini (ensure GEMINI_API_KEY is set if API_PROVIDER is gemini):")
    os.environ["API_PROVIDER"] = "gemini"
    # Ensure GEMINI_API_KEY is set in your environment for this to pass
    if not os.getenv("GEMINI_API_KEY"):
        print("GEMINI_API_KEY not set, skipping Gemini client instantiation for this test.")
    else:
        try:
            gemini_client = get_llm_client()
            print(f"Gemini client: {type(gemini_client)}")
        except ValueError as e:
            print(f"Error: {e}")

    print("\nTesting Ollama:")
    os.environ["API_PROVIDER"] = "ollama"
    try:
        ollama_client = get_llm_client()
        print(f"Ollama client: {type(ollama_client)}")
        print(f"  Base URL: {ollama_client.client.base_url}")
        print(f"  API Key: {ollama_client.client.api_key}")

    except ValueError as e:
        print(f"Error: {e}")

    # Test invalid provider (though get_api_provider defaults to gemini)
    # To properly test this, get_api_provider would need to not have a default.
    # For now, this will likely default to gemini and potentially fail if GEMINI_API_KEY is not set.
    # print("\nTesting Invalid Provider (simulated):")
    # os.environ["API_PROVIDER"] = "unknown_provider"
    # try:
    #     client = get_llm_client()
    #     print(f"Client type for 'unknown_provider': {type(client)}")
    # except ValueError as e:
    #     print(f"Error for 'unknown_provider': {e}")

    # Clean up environment variable for subsequent tests if any
    if "API_PROVIDER" in os.environ:
        del os.environ["API_PROVIDER"]
