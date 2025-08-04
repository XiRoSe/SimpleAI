"""
Global configuration management for SimpleAI.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union, List, AsyncGenerator, Generator
from dataclasses import dataclass, field

from .exceptions import ConfigurationError, APIError, ProviderError
from .utils import load_env_file, sanitize_message_content, merge_dicts


# Load environment variables on import
load_env_file()

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Configuration data structure."""
    api_key: Optional[str] = None
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: int = 30
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "max_retries": self.max_retries
        }


class SimpleAI:
    """
    Global configuration and chat interface for SimpleAI.
    
    This class provides:
    - Global configuration management
    - Direct chat capabilities
    - Provider abstraction (OpenAI, Claude)
    """
    
    # Class-level configuration
    _config: Optional[Config] = None
    _openai_client: Optional[Any] = None
    _anthropic_client: Optional[Any] = None
    
    @classmethod
    def configure(
        cls,
        api_key: Optional[str] = None,
        provider: str = "openai",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        timeout: int = 30,
        max_retries: int = 3
    ) -> None:
        """
        Configure SimpleAI globally.
        
        Args:
            api_key: API key for the provider (auto-detected from env if not provided)
            provider: AI provider ("openai" or "claude")
            model: Model to use (defaults based on provider)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Auto-detect API key from environment
        if not api_key:
            if provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
            elif provider == "claude":
                api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not api_key:
            raise ConfigurationError(
                f"API key required for {provider}. "
                f"Set {'OPENAI_API_KEY' if provider == 'openai' else 'ANTHROPIC_API_KEY'} "
                "environment variable or pass api_key parameter."
            )
        
        # Default models based on provider
        if not model:
            model = "gpt-4o" if provider == "openai" else "claude-3-5-sonnet-20241022"
        
        # Validate configuration
        cls._validate_config(provider, model, temperature)
        
        # Create configuration
        cls._config = Config(
            api_key=api_key,
            provider=provider,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            max_retries=max_retries
        )
        
        # Initialize clients
        cls._initialize_clients()
        
        logger.info(f"SimpleAI configured for provider: {provider}, model: {model}")
    
    @classmethod
    def _validate_config(cls, provider: str, model: str, temperature: float) -> None:
        """Validate configuration parameters."""
        if provider not in ["openai", "claude"]:
            raise ConfigurationError("Provider must be 'openai' or 'claude'")
        
        if not 0 <= temperature <= 2:
            raise ConfigurationError("Temperature must be between 0 and 2")
        
        # Validate model names
        openai_models = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo", "gpt-4-turbo"]
        claude_models = ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"]
        
        if provider == "openai" and model not in openai_models:
            logger.warning(f"Unknown OpenAI model: {model}")
        elif provider == "claude" and model not in claude_models:
            logger.warning(f"Unknown Claude model: {model}")
    
    @classmethod
    def _initialize_clients(cls) -> None:
        """Initialize API clients based on provider."""
        if not cls._config:
            return
            
        # Reset existing clients
        cls._openai_client = None
        cls._anthropic_client = None
        
        if cls._config.provider == "openai":
            try:
                from openai import OpenAI
                cls._openai_client = OpenAI(
                    api_key=cls._config.api_key,
                    timeout=cls._config.timeout,
                    max_retries=cls._config.max_retries
                )
            except ImportError:
                raise ConfigurationError("OpenAI package not installed. Run: pip install openai>=1.0.0")
        
        elif cls._config.provider == "claude":
            try:
                from anthropic import Anthropic
                cls._anthropic_client = Anthropic(
                    api_key=cls._config.api_key,
                    timeout=cls._config.timeout,
                    max_retries=cls._config.max_retries
                )
            except ImportError:
                raise ConfigurationError("Anthropic package not installed. Run: pip install anthropic>=0.25.0")
    
    @classmethod
    def get_config(cls) -> Optional[Config]:
        """Get current configuration."""
        return cls._config
    
    @classmethod
    def chat(
        cls,
        messages: Union[str, List[Dict[str, Any]]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        stream: bool = False
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Send a chat message and get a response.
        
        Args:
            messages: String message or list of message dicts
            tools: Optional list of tool definitions
            model: Override configured model
            temperature: Override configured temperature
            stream: Enable streaming responses
            
        Returns:
            Response string or stream generator
            
        Raises:
            ConfigurationError: If SimpleAI not configured
            APIError: If API call fails
        """
        if not cls._config:
            raise ConfigurationError("SimpleAI not configured. Call SimpleAI.configure() first.")
        
        # Convert string to message list
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        # Build parameters
        params = {
            "model": model or cls._config.model,
            "temperature": temperature if temperature is not None else cls._config.temperature,
            "messages": messages
        }
        
        if cls._config.max_tokens:
            params["max_tokens"] = cls._config.max_tokens
        
        if tools:
            params["tools"] = tools
        
        if stream:
            params["stream"] = True
        
        # Route to appropriate provider
        if cls._config.provider == "openai":
            return cls._chat_openai(params)
        else:
            return cls._chat_claude(params)
    
    @classmethod
    def _chat_openai(cls, params: Dict[str, Any]) -> str:
        """Handle OpenAI chat completion."""
        if not cls._openai_client:
            raise ProviderError("OpenAI client not initialized")
        
        try:
            response = cls._openai_client.chat.completions.create(**params)
            
            if params.get("stream"):
                return cls._stream_openai(response)
            
            # Extract content from response
            message = response.choices[0].message
            
            # Handle tool calls
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tool_calls = []
                for tool_call in message.tool_calls:
                    tool_calls.append({
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    })
                return {"content": message.content or "", "tool_calls": tool_calls}
            
            return message.content or ""
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise APIError(f"OpenAI API error: {e}")

    @classmethod
    def _chat_claude(cls, params: Dict[str, Any]) -> str:
        """Handle Claude chat completion."""
        if not cls._anthropic_client:
            raise ProviderError("Anthropic client not initialized")

        try:
            # Convert messages to Claude format
            claude_messages = []
            system_prompt = None

            for msg in params["messages"]:
                if msg["role"] == "system":
                    system_prompt = msg["content"]
                else:
                    claude_messages.append({
                        "role": msg["role"],
                        "content": sanitize_message_content(msg["content"])
                    })

            # Build Claude parameters
            claude_params = {
                "model": params["model"],
                "messages": claude_messages,
                "temperature": params["temperature"],
                "max_tokens": params.get("max_tokens", 4096)  # Claude requires max_tokens
            }

            if system_prompt:
                claude_params["system"] = system_prompt

            # Convert tools to Claude format
            if params.get("tools"):
                claude_params["tools"] = [
                    {
                        "name": tool["function"]["name"],
                        "description": tool["function"]["description"],
                        "input_schema": tool["function"]["parameters"]
                    }
                    for tool in params["tools"]
                ]

            response = cls._anthropic_client.messages.create(**claude_params)

            # Extract content from response
            content_parts = []
            tool_calls = []

            for content_block in response.content:
                if content_block.type == "text":
                    content_parts.append(content_block.text)
                elif content_block.type == "tool_use":
                    tool_calls.append({
                        "id": content_block.id,
                        "name": content_block.name,
                        "arguments": json.dumps(content_block.input)
                    })

            if tool_calls:
                return {
                    "content": " ".join(content_parts),
                    "tool_calls": tool_calls
                }

            return " ".join(content_parts)

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise APIError(f"Claude API error: {e}")

    @classmethod
    async def achat(
        cls,
        messages: Union[str, List[Dict[str, Any]]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        stream: bool = False
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Async version of chat method.

        Args:
            Same as chat()

        Returns:
            Response string or async stream generator
        """
        if not cls._config:
            raise ConfigurationError("SimpleAI not configured. Call SimpleAI.configure() first.")

        # Convert string to message list
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        # Build parameters
        params = {
            "model": model or cls._config.model,
            "temperature": temperature if temperature is not None else cls._config.temperature,
            "messages": messages
        }

        if cls._config.max_tokens:
            params["max_tokens"] = cls._config.max_tokens

        if tools:
            params["tools"] = tools

        if stream:
            params["stream"] = True

        # Route to appropriate provider
        if cls._config.provider == "openai":
            return await cls._achat_openai(params)
        else:
            return await cls._achat_claude(params)
    
    @classmethod
    async def _achat_openai(cls, params: Dict[str, Any]) -> str:
        """Async OpenAI chat completion."""
        if not cls._openai_client:
            raise ProviderError("OpenAI client not initialized")
        
        try:
            from openai import AsyncOpenAI
            
            # Create async client if needed
            if not hasattr(cls, '_async_openai_client'):
                cls._async_openai_client = AsyncOpenAI(
                    api_key=cls._config.api_key,
                    timeout=cls._config.timeout,
                    max_retries=cls._config.max_retries
                )
            
            response = await cls._async_openai_client.chat.completions.create(**params)
            
            if params.get("stream"):
                return cls._astream_openai(response)
            
            # Extract content from response
            message = response.choices[0].message
            
            # Handle tool calls
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tool_calls = []
                for tool_call in message.tool_calls:
                    tool_calls.append({
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    })
                return {"content": message.content or "", "tool_calls": tool_calls}
            
            return message.content or ""
            
        except Exception as e:
            logger.error(f"OpenAI async API error: {e}")
            raise APIError(f"OpenAI async API error: {e}")
    
    @classmethod
    async def _achat_claude(cls, params: Dict[str, Any]) -> str:
        """Async Claude chat completion."""
        if not cls._anthropic_client:
            raise ProviderError("Anthropic client not initialized")
        
        try:
            from anthropic import AsyncAnthropic
            import json
            
            # Create async client if needed
            if not hasattr(cls, '_async_anthropic_client'):
                cls._async_anthropic_client = AsyncAnthropic(
                    api_key=cls._config.api_key,
                    timeout=cls._config.timeout,
                    max_retries=cls._config.max_retries
                )
            
            # Convert messages to Claude format
            claude_messages = []
            system_prompt = None
            
            for msg in params["messages"]:
                if msg["role"] == "system":
                    system_prompt = msg["content"]
                else:
                    claude_messages.append({
                        "role": msg["role"],
                        "content": sanitize_message_content(msg["content"])
                    })
            
            # Build Claude parameters
            claude_params = {
                "model": params["model"],
                "messages": claude_messages,
                "temperature": params["temperature"],
                "max_tokens": params.get("max_tokens", 4096)
            }
            
            if system_prompt:
                claude_params["system"] = system_prompt
            
            # Convert tools to Claude format
            if params.get("tools"):
                claude_params["tools"] = [
                    {
                        "name": tool["function"]["name"],
                        "description": tool["function"]["description"],
                        "input_schema": tool["function"]["parameters"]
                    }
                    for tool in params["tools"]
                ]
            
            response = await cls._async_anthropic_client.messages.create(**claude_params)
            
            # Extract content from response
            content_parts = []
            tool_calls = []
            
            for content_block in response.content:
                if content_block.type == "text":
                    content_parts.append(content_block.text)
                elif content_block.type == "tool_use":
                    tool_calls.append({
                        "id": content_block.id,
                        "name": content_block.name,
                        "arguments": json.dumps(content_block.input)
                    })
            
            if tool_calls:
                return {
                    "content": " ".join(content_parts),
                    "tool_calls": tool_calls
                }
            
            return " ".join(content_parts)
            
        except Exception as e:
            logger.error(f"Claude async API error: {e}")
            raise APIError(f"Claude async API error: {e}")
    
    @classmethod
    def _stream_openai(cls, response) -> Generator[str, None, None]:
        """Handle OpenAI streaming responses."""
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    @classmethod
    async def _astream_openai(cls, response) -> AsyncGenerator[str, None]:
        """Handle OpenAI async streaming responses."""
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content