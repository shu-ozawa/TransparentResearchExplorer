import unittest
from unittest.mock import patch, MagicMock
import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from io import StringIO

# Using direct import assuming PYTHONPATH is set correctly for tests
from backend.app.clients.gemini_client import GeminiClient
from google.api_core import exceptions as google_exceptions # For specific API errors

# Global mock for genai module
mock_genai_module = MagicMock()

# Default model name used in GeminiClient
DEFAULT_GEMINI_MODEL = 'gemini-2.5-flash-preview-05-20'

@patch('backend.app.clients.gemini_client.genai', new=mock_genai_module)
class TestGeminiClient(unittest.TestCase):

    def setUp(self):
        # Reset mocks for each test to ensure isolation
        mock_genai_module.reset_mock()
        
        # Mock for the GenerativeModel instance
        self.mock_model_instance = MagicMock()
        mock_genai_module.GenerativeModel.return_value = self.mock_model_instance
        
        # Mock for the response object from generate_content
        self.mock_response = MagicMock()
        # Configure default successful response
        self.mock_response.text = "Generated text"
        # Ensure parts attribute exists and is iterable, and parts have text attribute
        mock_part = MagicMock()
        mock_part.text = "Generated text from part"
        self.mock_response.parts = [mock_part]
        
        self.mock_model_instance.generate_content.return_value = self.mock_response
        # Clear any side effects from previous tests
        self.mock_model_instance.generate_content.side_effect = None

        # Capture stderr
        self.held_stderr = sys.stderr
        sys.stderr = StringIO()
        
        # Common API key for tests
        self.test_api_key = "test_api_key_123"

    def tearDown(self):
        sys.stderr = self.held_stderr

    def test_initialization_success(self):
        """Test successful initialization configures genai."""
        GeminiClient(api_key=self.test_api_key)
        mock_genai_module.configure.assert_called_once_with(api_key=self.test_api_key)

    def test_initialization_failure_no_api_key(self):
        """Test initialization fails if api_key is empty."""
        with self.assertRaisesRegex(ValueError, "Gemini API key must be provided."):
            GeminiClient(api_key="") # Pass an empty string

    def test_generate_text_success_with_default_model(self):
        """Test successful text generation using the default model."""
        client = GeminiClient(api_key=self.test_api_key)
        prompt = "Test prompt"
        
        result = client.generate_text(prompt)
        
        mock_genai_module.GenerativeModel.assert_called_once_with(DEFAULT_GEMINI_MODEL)
        self.mock_model_instance.generate_content.assert_called_once_with(prompt)
        self.assertEqual(result, "Generated text")

    def test_generate_text_success_with_custom_model(self):
        """Test successful text generation using a custom model."""
        client = GeminiClient(api_key=self.test_api_key)
        prompt = "Test prompt for custom model"
        custom_model = "gemini-custom-model"
        
        result = client.generate_text(prompt, model=custom_model)
        
        mock_genai_module.GenerativeModel.assert_called_once_with(custom_model)
        self.mock_model_instance.generate_content.assert_called_once_with(prompt)
        self.assertEqual(result, "Generated text")

    def test_generate_text_api_error(self):
        """Test handling of GoogleAPIError during text generation."""
        client = GeminiClient(api_key=self.test_api_key)
        self.mock_model_instance.generate_content.side_effect = google_exceptions.GoogleAPIError("Simulated API Error")

        prompt = "Test prompt for API error"
        result = client.generate_text(prompt)
        
        self.assertEqual(result, "")
        self.assertIn("Gemini API Error: Simulated API Error", sys.stderr.getvalue())

    def test_generate_text_unexpected_error(self):
        """Test handling of unexpected errors during text generation."""
        client = GeminiClient(api_key=self.test_api_key)
        self.mock_model_instance.generate_content.side_effect = RuntimeError("Unexpected runtime error")

        prompt = "Test prompt for runtime error"
        result = client.generate_text(prompt)
        
        self.assertEqual(result, "")
        self.assertIn("An unexpected error occurred: Unexpected runtime error", sys.stderr.getvalue())
            
    def test_generate_text_empty_response_text_uses_parts(self):
        """Test that text from parts is used if response.text is None."""
        client = GeminiClient(api_key=self.test_api_key)
        
        mock_response_empty_text = MagicMock()
        mock_response_empty_text.text = None # text is None
        
        mock_part_content = "Text from parts only"
        mock_part = MagicMock()
        mock_part.text = mock_part_content
        mock_response_empty_text.parts = [mock_part] # parts has text
        
        self.mock_model_instance.generate_content.return_value = mock_response_empty_text
        
        prompt = "Test prompt for empty text attribute"
        result = client.generate_text(prompt)
        self.assertEqual(result, mock_part_content)

    def test_generate_text_empty_response_text_and_empty_parts_text(self):
        """Test response handling when response.text is None and part.text is also None/empty."""
        client = GeminiClient(api_key=self.test_api_key)
        
        mock_response_all_empty = MagicMock()
        mock_response_all_empty.text = None
        
        mock_empty_part = MagicMock()
        mock_empty_part.text = "" # Part text is empty
        mock_response_all_empty.parts = [mock_empty_part]
        
        self.mock_model_instance.generate_content.return_value = mock_response_all_empty
        
        prompt = "Test prompt for all empty text"
        result = client.generate_text(prompt)
        self.assertEqual(result, "") # Should return empty string
        self.assertIn("Gemini API Error: Empty response or text unavailable.", sys.stderr.getvalue())

    def test_generate_text_no_text_and_no_parts_attribute(self):
        """Test response handling when response.text is None and response.parts attribute is missing."""
        client = GeminiClient(api_key=self.test_api_key)
        
        mock_response_no_parts_attr = MagicMock()
        mock_response_no_parts_attr.text = None
        # Simulate 'parts' attribute not existing or being None
        # One way is to make it a property that raises AttributeError or simply set to None
        # For MagicMock, if an attribute is not set, accessing it creates a new MagicMock.
        # To simulate it "not being there" in a way that hasattr would fail, or for an empty list:
        mock_response_no_parts_attr.parts = [] # No parts available
        
        self.mock_model_instance.generate_content.return_value = mock_response_no_parts_attr
        
        prompt = "Test prompt for no parts attribute"
        result = client.generate_text(prompt)
        self.assertEqual(result, "")
        self.assertIn("Gemini API Error: Empty response or text unavailable.", sys.stderr.getvalue())

if __name__ == '__main__':
    unittest.main()
