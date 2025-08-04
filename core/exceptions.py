"""
Custom exceptions for SimpleAI framework.
"""


class SimpleAIError(Exception):
    """Base exception for all SimpleAI errors."""
    pass


class ConfigurationError(SimpleAIError):
    """Raised when SimpleAI is not configured or configuration is invalid."""
    pass


class APIError(SimpleAIError):
    """Raised when API calls fail."""
    pass


class ToolError(SimpleAIError):
    """Raised when tool execution fails."""
    pass


class ProviderError(SimpleAIError):
    """Raised when provider-specific operations fail."""
    pass


class ValidationError(SimpleAIError):
    """Raised when input validation fails."""
    pass