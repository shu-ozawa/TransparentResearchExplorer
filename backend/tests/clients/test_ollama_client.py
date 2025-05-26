import pytest
from unittest.mock import patch, MagicMock
import openai # For openai.APIError
import sys

from backend.app.clients.ollama_client import OllamaClient

class TestOllamaClient:

    @patch('backend.app.clients.ollama_client.openai.OpenAI')
    def test_ollama_client_initialization(self, mock_openai_class: MagicMock):
        """Test that OllamaClient initializes openai.OpenAI with correct parameters."""
        expected_base_url = "http://localhost:1234/v1"
        expected_api_key = "testkey123"

        OllamaClient(base_url=expected_base_url, api_key=expected_api_key)

        mock_openai_class.assert_called_once_with(
            base_url=expected_base_url,
            api_key=expected_api_key
        )

    @patch('backend.app.clients.ollama_client.openai.OpenAI')
    def test_generate_text_success(self, mock_openai_class: MagicMock):
        """Test successful text generation."""
        mock_client_instance = MagicMock() # This is the mock for openai.OpenAI()
        mock_chat_completions_instance = MagicMock() # This is for client.chat.completions
        
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "  Generated llama3 text  " # With spaces to test strip()
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        mock_chat_completions_instance.create.return_value = mock_response
        mock_client_instance.chat.completions = mock_chat_completions_instance
        mock_openai_class.return_value = mock_client_instance

        client = OllamaClient(base_url="http://test.ollama.url/v1", api_key="test_key")
        
        prompt = "What is the capital of Ollama-land?"
        model = "llama3-test"
        expected_messages = [{"role": "user", "content": prompt}]
        
        result = client.generate_text(prompt=prompt, model=model)

        mock_chat_completions_instance.create.assert_called_once_with(
            model=model,
            messages=expected_messages
        )
        assert result == "Generated llama3 text"

    @patch('backend.app.clients.ollama_client.openai.OpenAI')
    def test_generate_text_api_error(self, mock_openai_class: MagicMock, capsys):
        """Test API error handling during text generation."""
        mock_client_instance = MagicMock()
        mock_chat_completions_instance = MagicMock()
        mock_chat_completions_instance.create.side_effect = openai.APIError("Test API Error", request=None, body=None)
        mock_client_instance.chat.completions = mock_chat_completions_instance
        mock_openai_class.return_value = mock_client_instance

        client = OllamaClient(base_url="http://test.ollama.url/v1", api_key="test_key")
        result = client.generate_text(prompt="A prompt that will fail")

        assert result == ""
        captured = capsys.readouterr()
        assert "Ollama API Error: Test API Error" in captured.err

    @patch('backend.app.clients.ollama_client.openai.OpenAI')
    def test_generate_text_empty_choices(self, mock_openai_class: MagicMock, capsys):
        """Test handling of response with empty choices list."""
        mock_client_instance = MagicMock()
        mock_chat_completions_instance = MagicMock()
        
        mock_response = MagicMock()
        mock_response.choices = [] # Empty choices
        
        mock_chat_completions_instance.create.return_value = mock_response
        mock_client_instance.chat.completions = mock_chat_completions_instance
        mock_openai_class.return_value = mock_client_instance

        client = OllamaClient(base_url="http://test.ollama.url/v1", api_key="test_key")
        result = client.generate_text(prompt="A prompt")

        assert result == ""
        captured = capsys.readouterr()
        assert "Error: No response choices or message content found." in captured.err

    @patch('backend.app.clients.ollama_client.openai.OpenAI')
    def test_generate_text_no_message_content(self, mock_openai_class: MagicMock, capsys):
        """Test handling of response where message content is missing."""
        mock_client_instance = MagicMock()
        mock_chat_completions_instance = MagicMock()
        
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = None # No content
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        mock_chat_completions_instance.create.return_value = mock_response
        mock_client_instance.chat.completions = mock_chat_completions_instance
        mock_openai_class.return_value = mock_client_instance

        client = OllamaClient(base_url="http://test.ollama.url/v1", api_key="test_key")
        result = client.generate_text(prompt="A prompt")

        assert result == ""
        # Depending on implementation, this might also log the "No response choices or message content found" or similar
        captured = capsys.readouterr()
        # Check if the specific log for empty content (after choice exists) is present
        # The current implementation returns "" if content is None, which is fine.
        # The error "No response choices or message content found." is for when choice or choice.message is None.
        # If content is None, it should just return "" without a specific error log for that part.
        # If content is an empty string, it should also return "" (due to strip).
        # Let's verify that no specific error is printed for *this particular case* of content=None
        # but if choices[0].message itself was None, then the other error would appear.
        # The current code: `content = response.choices[0].message.content; return content.strip() if content else ""`
        # This handles `content is None` or `content == ""` by returning `""`.
        # Let's test the case where `choices[0].message` is None
        
        mock_choice_no_message = MagicMock()
        mock_choice_no_message.message = None # Message object is None
        mock_response_no_message_obj = MagicMock()
        mock_response_no_message_obj.choices = [mock_choice_no_message]
        mock_chat_completions_instance.create.return_value = mock_response_no_message_obj
        
        result_no_msg_obj = client.generate_text(prompt="Another prompt")
        assert result_no_msg_obj == ""
        captured_no_msg_obj = capsys.readouterr()
        assert "Error: No response choices or message content found." in captured_no_msg_obj.err


    @patch('backend.app.clients.ollama_client.openai.OpenAI')
    def test_generate_text_unexpected_error(self, mock_openai_class: MagicMock, capsys):
        """Test handling of unexpected errors during text generation."""
        mock_client_instance = MagicMock()
        mock_chat_completions_instance = MagicMock()
        mock_chat_completions_instance.create.side_effect = Exception("Unexpected spooky error")
        mock_client_instance.chat.completions = mock_chat_completions_instance
        mock_openai_class.return_value = mock_client_instance

        client = OllamaClient(base_url="http://test.ollama.url/v1", api_key="test_key")
        result = client.generate_text(prompt="A prompt that causes unknown failure")

        assert result == ""
        captured = capsys.readouterr()
        assert "An unexpected error occurred: Unexpected spooky error" in captured.err

    def test_ollama_client_initialization_missing_base_url(self):
        """Test OllamaClient initialization fails with missing base_url."""
        with pytest.raises(ValueError) as excinfo:
            OllamaClient(base_url="", api_key="test_key")
        assert "Ollama base_url must be provided." in str(excinfo.value)

        # api_key can be "ollama" or other non-empty strings, so not testing missing api_key
        # as it has a default mechanism in the original design (though now passed in).
        # The current class constructor doesn't prevent empty api_key, it's openai lib's job.
        # We are testing our class's explicit check for base_url.
        
    @patch('backend.app.clients.ollama_client.openai.OpenAI')
    def test_generate_text_model_parameter(self, mock_openai_class: MagicMock):
        """Test that the model parameter is correctly passed."""
        mock_client_instance = MagicMock()
        mock_chat_completions_instance = MagicMock()
        
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Generated text from specific model"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        mock_chat_completions_instance.create.return_value = mock_response
        mock_client_instance.chat.completions = mock_chat_completions_instance
        mock_openai_class.return_value = mock_client_instance

        client = OllamaClient(base_url="http://test.ollama.url/v1", api_key="test_key")
        
        prompt = "Test prompt"
        custom_model = "codellama-test"
        default_model = "llama3" # Default in OllamaClient.generate_text

        # Test with custom model
        client.generate_text(prompt=prompt, model=custom_model)
        mock_chat_completions_instance.create.assert_called_with(
            model=custom_model,
            messages=[{"role": "user", "content": prompt}]
        )

        # Test with default model
        client.generate_text(prompt=prompt) # Should use "llama3"
        mock_chat_completions_instance.create.assert_called_with(
            model=default_model,
            messages=[{"role": "user", "content": prompt}]
        )
