import sys
import openai

class OllamaClient:
    def __init__(self, base_url: str, api_key: str):
        """
        Initializes the OllamaClient.
        It configures the openai.OpenAI client to connect to a local Ollama instance
        using the provided base_url and api_key.
        """
        if not base_url:
            raise ValueError("Ollama base_url must be provided.")
        # api_key can sometimes be optional or a default like "ollama"
        # if not api_key:
        #     raise ValueError("Ollama api_key must be provided.")

        self.client = openai.OpenAI(
            base_url=base_url,
            api_key=api_key,
        )

    def generate_text(self, prompt: str, model: str = "llama3") -> str:
        """
        Generates text using the Ollama API.

        Args:
            prompt: The input prompt for the language model.
            model: The model to use for generation (e.g., "llama3").

        Returns:
            The generated text as a string, or an empty string if an error occurs
            or the response is empty.
        """
        messages = [{"role": "user", "content": prompt}]

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
            )
            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content
                return content.strip() if content else ""
            else:
                print("Error: No response choices or message content found.", file=sys.stderr)
                return ""
        except openai.APIError as e:
            print(f"Ollama API Error: {e}", file=sys.stderr)
            return ""
        except Exception as e:
            print(f"An unexpected error occurred: {e}", file=sys.stderr)
            return ""

if __name__ == '__main__':
    # Example usage (requires Ollama server to be running and appropriate config)
    # This example would now need to be run differently, perhaps by setting up
    # the client manually with parameters if you want to test it directly.
    # For example:
    # try:
    #     # This assumes you have OLLAMA_BASE_URL and OLLAMA_API_KEY in your env
    #     # or you provide them directly for testing.
    #     # For this example, let's use typical defaults if not set.
    #     import os
    #     test_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    #     test_api_key = os.getenv("OLLAMA_API_KEY", "ollama")
    #
    #     client = OllamaClient(base_url=test_base_url, api_key=test_api_key)
    #     prompt = "What is the capital of France?"
    #     print(f"Prompt: {prompt}")
    #     generated_text = client.generate_text(prompt)
    #     print(f"Generated text: {generated_text}")
    #
    #     prompt_code = "Write a simple python function to add two numbers."
    #     print(f"Prompt: {prompt_code}")
    #     # Ensure 'codellama' model is pulled in your Ollama instance
    #     generated_code = client.generate_text(prompt_code, model="codellama")
    #     print(f"Generated code: {generated_code}")
    #
    # except openai.APIConnectionError as e:
    #     print(f"Connection Error: Could not connect to Ollama at {test_base_url}", file=sys.stderr)
    #     print("Please ensure your Ollama server is running and accessible.", file=sys.stderr)
    # except Exception as e:
    #     print(f"Error during example usage: {e}", file=sys.stderr)
    #     print("Ensure Ollama is running and models (e.g., llama3, codellama) are pulled.", file=sys.stderr)
    pass # Keep the __main__ block, but adjust or comment out its content
