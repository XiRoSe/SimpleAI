"""
SimpleAI - Powerful Simplicity for AI Agents

A lightweight, production-ready framework for building AI agents with tool capabilities.
Enterprise-grade capabilities with the simplest possible API.
"""

from .config import SimpleAI
from .agent import SimpleAgent, SimpleTool
from .collaborate import SimpleCollaborate
from .exceptions import ConfigurationError, ToolError, APIError

__version__ = "0.1.0"
__all__ = [
    "SimpleAI",
    "SimpleAgent", 
    "SimpleTool",
    "SimpleCollaborate",
    "ConfigurationError",
    "ToolError", 
    "APIError"
]