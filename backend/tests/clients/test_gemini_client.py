import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from io import StringIO

# Adjust the import path based on your project structure
# This assumes backend/app/clients/gemini_client.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.clients.gemini_client import GeminiClient 

mock_genai = MagicMock()

@patch.dict(os.environ, {"GEMINI_API_KEY": "test_api_key"})
@patch('app.clients.gemini_client.genai', new=mock_genai)
class TestGeminiClientSuccess(unittest.TestCase):

    def setUp(self):
        mock_genai.reset_mock()
        
        self.mock_model_instance = MagicMock()
        mock_genai.GenerativeModel.return_value = self.mock_model_instance
        
        self.mock_response = MagicMock()
        self.mock_response.text = "Generated text"
        self.mock_response.parts = [MagicMock(text="Generated text")] # As per prompt for this class
        
        # Default behavior for the shared mock_model_instance
        self.mock_model_instance.generate_content.return_value = self.mock_response

    def test_initialization_success(self):
        client = GeminiClient()
        mock_genai.configure.assert_called_once_with(api_key="test_api_key")
        self.assertIsNotNone(client)

    def test_generate_text_success(self):
        client = GeminiClient()
        # self.mock_model_instance.generate_content is already configured in setUp 
        # to return self.mock_response by default.

        prompt = "Test prompt"
        result = client.generate_text(prompt)
        
        mock_genai.GenerativeModel.assert_called_once_with('gemini-pro')
        self.mock_model_instance.generate_content.assert_called_once_with(prompt)
        self.assertEqual(result, "Generated text")

class TestGeminiClientInitializationFailure(unittest.TestCase):

    @patch.dict(os.environ, {}, clear=True)
    @patch('app.clients.gemini_client.genai', new=MagicMock()) 
    def test_initialization_failure_no_api_key(self):
        with self.assertRaisesRegex(ValueError, "GEMINI_API_KEY environment variable not set."):
            GeminiClient()

@patch.dict(os.environ, {"GEMINI_API_KEY": "test_api_key"})
@patch('app.clients.gemini_client.genai', new=mock_genai)
class TestGeminiClientApiFailures(unittest.TestCase):

    def setUp(self):
        mock_genai.reset_mock()
        mock_genai.configure = MagicMock() # Ensure configure is a fresh mock for assertions like assert_called_once_with
        
        self.mock_model_instance = MagicMock()
        mock_genai.GenerativeModel.return_value = self.mock_model_instance
        
        self.held_stderr = sys.stderr
        sys.stderr = StringIO()

    def tearDown(self):
        sys.stderr = self.held_stderr

    def test_generate_text_api_error(self):
        client = GeminiClient()
        # Configure the shared mock_model_instance for this specific test
        self.mock_model_instance.generate_content.side_effect = Exception("Simulated API Error")

        prompt = "Test prompt for API error"
        result = client.generate_text(prompt)
        self.assertEqual(result, "")
        self.assertIn("An unexpected error occurred: Simulated API Error", sys.stderr.getvalue())

    def test_generate_text_unexpected_error(self):
        client = GeminiClient()
        # Configure the shared mock_model_instance for this specific test
        self.mock_model_instance.generate_content.side_effect = RuntimeError("Unexpected runtime error")

        prompt = "Test prompt for runtime error"
        result = client.generate_text(prompt)
        self.assertEqual(result, "")
        self.assertIn("An unexpected error occurred: Unexpected runtime error", sys.stderr.getvalue())
            
    def test_generate_text_empty_response_text_uses_parts(self):
        client = GeminiClient()
        mock_genai.configure.assert_called_once_with(api_key="test_api_key")

        mock_response_empty_text = MagicMock()
        mock_response_empty_text.text = None 
        mock_response_empty_text.parts = [MagicMock(text="Text from parts")] # As per prompt
        
        # Configure the shared mock_model_instance for this specific test
        self.mock_model_instance.generate_content.return_value = mock_response_empty_text
        # Reset side_effect if it was set in a previous test using the same instance
        self.mock_model_instance.generate_content.side_effect = None 
        
        prompt = "Test prompt for empty text"
        result = client.generate_text(prompt)
        self.assertEqual(result, "Text from parts")

if __name__ == '__main__':
    unittest.main()
