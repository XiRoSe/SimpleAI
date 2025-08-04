"""
Tests for SimpleAI configuration.
"""

import pytest
from unittest.mock import Mock, patch
from core import SimpleAI
from core.exceptions import ConfigurationError


class TestSimpleAIConfig:
    """Test SimpleAI configuration functionality."""
    
    def setup_method(self):
        """Reset configuration before each test."""
        SimpleAI._config = None
        SimpleAI._openai_client = None
        SimpleAI._anthropic_client = None
    
    @patch('builtins.__import__')
    def test_configure_with_api_key(self, mock_import):
        """Test configuration with explicit API key."""
        # Mock the import
        def import_side_effect(name, *args, **kwargs):
            if name == 'openai':
                mock_module = Mock()
                mock_module.OpenAI = Mock()
                return mock_module
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = import_side_effect
        
        SimpleAI.configure(
            api_key="test-key",
            provider="openai",
            model="gpt-4o",
            temperature=0.5
        )
        
        config = SimpleAI.get_config()
        assert config is not None
        assert config.api_key == "test-key"
        assert config.provider == "openai"
        assert config.model == "gpt-4o"
        assert config.temperature == 0.5
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'env-test-key'})
    @patch('builtins.__import__')
    def test_configure_with_env_key(self, mock_import):
        """Test configuration with environment variable."""
        # Mock the import
        def import_side_effect(name, *args, **kwargs):
            if name == 'openai':
                mock_module = Mock()
                mock_module.OpenAI = Mock()
                return mock_module
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = import_side_effect
        
        SimpleAI.configure(provider="openai")
        
        config = SimpleAI.get_config()
        assert config is not None
        assert config.api_key == "env-test-key"
    
    def test_configure_invalid_provider(self):
        """Test configuration with invalid provider."""
        with pytest.raises(ConfigurationError) as exc_info:
            SimpleAI.configure(
                api_key="test-key",
                provider="invalid"
            )
        assert "Provider must be" in str(exc_info.value)
    
    def test_configure_invalid_temperature(self):
        """Test configuration with invalid temperature."""
        with pytest.raises(ConfigurationError) as exc_info:
            SimpleAI.configure(
                api_key="test-key",
                provider="openai",
                temperature=3.0
            )
        assert "Temperature must be between" in str(exc_info.value)
    
    @patch('builtins.__import__')
    def test_configure_no_api_key(self, mock_import):
        """Test configuration without API key."""
        # Mock the import so we don't hit ImportError
        def import_side_effect(name, *args, **kwargs):
            if name == 'openai':
                mock_module = Mock()
                mock_module.OpenAI = Mock()
                return mock_module
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = import_side_effect
        
        with pytest.raises(ConfigurationError) as exc_info:
            SimpleAI.configure(provider="openai")
        assert "API key required" in str(exc_info.value)
    
    def test_chat_without_config(self):
        """Test chat without configuration."""
        with pytest.raises(ConfigurationError) as exc_info:
            SimpleAI.chat("Hello")
        assert "SimpleAI not configured" in str(exc_info.value)
    
    @patch('builtins.__import__')
    def test_chat_simple_message(self, mock_import):
        """Test chat with simple string message."""
        # Setup mock OpenAI module
        mock_openai_class = Mock()
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response", tool_calls=None))]
        mock_client.chat.completions.create.return_value = mock_response
        
        # Mock the import
        def import_side_effect(name, *args, **kwargs):
            if name == 'openai':
                mock_module = Mock()
                mock_module.OpenAI = mock_openai_class
                return mock_module
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = import_side_effect
        
        # Configure and chat
        SimpleAI.configure(api_key="test-key", provider="openai")
        response = SimpleAI.chat("Hello")
        
        assert response == "Test response"
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('builtins.__import__')
    def test_chat_with_messages(self, mock_import):
        """Test chat with message list."""
        # Setup mock OpenAI module
        mock_openai_class = Mock()
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response", tool_calls=None))]
        mock_client.chat.completions.create.return_value = mock_response
        
        # Mock the import
        def import_side_effect(name, *args, **kwargs):
            if name == 'openai':
                mock_module = Mock()
                mock_module.OpenAI = mock_openai_class
                return mock_module
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = import_side_effect
        
        # Configure and chat
        SimpleAI.configure(api_key="test-key", provider="openai")
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"}
        ]
        response = SimpleAI.chat(messages)
        
        assert response == "Test response"
    
    @patch('builtins.__import__')
    def test_default_models(self, mock_import):
        """Test default model selection."""
        # Mock the import
        def import_side_effect(name, *args, **kwargs):
            if name == 'openai':
                mock_module = Mock()
                mock_module.OpenAI = Mock()
                return mock_module
            elif name == 'anthropic':
                mock_module = Mock()
                mock_module.Anthropic = Mock()
                return mock_module
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = import_side_effect
        
        SimpleAI.configure(api_key="test-key", provider="openai")
        assert SimpleAI.get_config().model == "gpt-4o"
        
        SimpleAI._config = None
        SimpleAI.configure(api_key="test-key", provider="claude")
        assert SimpleAI.get_config().model == "claude-3-5-sonnet-20241022"