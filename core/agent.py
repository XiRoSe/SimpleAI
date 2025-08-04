"""
AI Agent implementation with tool capabilities.
"""

import json
import logging
import inspect
from typing import Dict, Any, Optional, List, Callable, Union, Tuple
from collections import deque
from functools import wraps

from .config import SimpleAI
from .exceptions import ConfigurationError, ToolError, ValidationError
from .utils import format_tool_schema, extract_json_from_string, sanitize_message_content


logger = logging.getLogger(__name__)


class SimpleTool:
    """
    Decorator for creating agent tools.
    
    Automatically extracts function signature and creates tool schema.
    """
    
    def __init__(self, description: str = "", validate_params: bool = True):
        """
        Initialize tool decorator.
        
        Args:
            description: Tool description
            validate_params: Whether to validate parameters at runtime
        """
        self.description = description
        self.validate_params = validate_params
    
    def __call__(self, func: Callable) -> Callable:
        """Decorate function as a tool."""
        # Extract function signature
        sig = inspect.signature(func)
        params = {}
        required = []
        
        # Build parameter schema
        properties = {}
        for name, param in sig.parameters.items():
            if name == "self":  # Skip self parameter
                continue
                
            # Determine parameter type
            param_schema = {"type": "string", "description": f"Parameter: {name}"}  # Default
            
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_schema = {"type": "integer", "description": f"Parameter: {name}"}
                elif param.annotation == float:
                    param_schema = {"type": "number", "description": f"Parameter: {name}"}
                elif param.annotation == bool:
                    param_schema = {"type": "boolean", "description": f"Parameter: {name}"}
                elif param.annotation == list:
                    param_schema = {
                        "type": "array",
                        "items": {"type": "number"},  # Default to numbers for list
                        "description": f"Parameter: {name}"
                    }
                elif param.annotation == dict:
                    param_schema = {"type": "object", "description": f"Parameter: {name}"}
                else:
                    # Handle typing annotations like List[int], List[str], etc.
                    import typing
                    if hasattr(param.annotation, '__origin__'):
                        if param.annotation.__origin__ is list:
                            # Extract item type from List[ItemType]
                            if hasattr(param.annotation, '__args__') and param.annotation.__args__:
                                item_type = param.annotation.__args__[0]
                                if item_type == int:
                                    items_schema = {"type": "integer"}
                                elif item_type == float:
                                    items_schema = {"type": "number"}
                                elif item_type == str:
                                    items_schema = {"type": "string"}
                                elif item_type == bool:
                                    items_schema = {"type": "boolean"}
                                else:
                                    items_schema = {"type": "string"}  # Default fallback
                            else:
                                items_schema = {"type": "string"}  # Default fallback
                            
                            param_schema = {
                                "type": "array",
                                "items": items_schema,
                                "description": f"Parameter: {name}"
                            }
            
            properties[name] = param_schema
            
            # Check if required
            if param.default == inspect.Parameter.empty:
                required.append(name)
        
        # Create parameter schema
        if properties:
            params = {
                "type": "object",
                "properties": properties,
                "required": required
            }
        else:
            params = {
                "type": "object",
                "properties": {}
            }
        
        # Create tool wrapper
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Validate parameters if enabled
                if self.validate_params and params.get("required"):
                    for req_param in params["required"]:
                        if req_param not in kwargs:
                            raise ValidationError(f"Required parameter '{req_param}' missing")
                
                # Execute function
                result = func(*args, **kwargs)
                logger.debug(f"Tool '{func.__name__}' executed successfully")
                return result
                
            except Exception as e:
                logger.error(f"Tool '{func.__name__}' failed: {e}")
                raise ToolError(f"Tool execution failed: {e}")
        
        # Attach metadata
        wrapper.tool_name = func.__name__
        wrapper.tool_description = self.description or func.__doc__ or f"Function: {func.__name__}"
        wrapper.tool_params = params
        wrapper.is_tool = True
        
        return wrapper


class SimpleAgent:
    """
    AI agent with tool capabilities and memory management.
    
    Uses global SimpleAI configuration automatically.
    """
    
    def __init__(
        self,
        system_prompt: str = "You are a helpful AI assistant.",
        tools: Optional[List[Callable]] = None,
        use_memory: bool = True,
        memory_size: int = 20,
        name: Optional[str] = None
    ):
        """
        Initialize agent.
        
        Args:
            system_prompt: System prompt defining agent behavior
            tools: List of tool functions (decorated with @SimpleTool)
            use_memory: Whether to maintain conversation memory
            memory_size: Maximum memory entries to retain
            name: Optional agent name
            
        Raises:
            ConfigurationError: If SimpleAI not configured
        """
        # Check if SimpleAI is configured
        if not SimpleAI.get_config():
            raise ConfigurationError("SimpleAI not configured. Call SimpleAI.configure() first.")
        
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.use_memory = use_memory
        self.name = name or "Agent"
        
        # Initialize memory
        self.memory: deque = deque(maxlen=memory_size) if use_memory else deque(maxlen=0)
        
        # Process tools
        self.tool_schemas = []
        self.tool_map = {}
        
        for tool in self.tools:
            if not hasattr(tool, 'is_tool') or not tool.is_tool:
                logger.warning(f"Function '{tool.__name__}' is not decorated with @SimpleTool")
                continue
            
            # Create tool schema
            schema = format_tool_schema(
                tool.tool_name,
                tool.tool_description,
                tool.tool_params
            )
            self.tool_schemas.append(schema)
            self.tool_map[tool.tool_name] = tool
        
        logger.info(f"Agent '{self.name}' initialized with {len(self.tool_schemas)} tools")
    
    def chat(self, message: str, stream: bool = False) -> str:
        """
        Send a message to the agent and get response.
        
        Args:
            message: User message
            stream: Enable streaming response
            
        Returns:
            Agent response
        """
        logger.debug(f"Agent '{self.name}' received message: {message[:100]}{'...' if len(message) > 100 else ''}")
        logger.debug(f"Agent '{self.name}' has {len(self.tool_schemas)} tools available: {[tool.get('function', {}).get('name', 'unknown') for tool in self.tool_schemas]}")
        
        # Build conversation messages
        messages = self._build_messages(message)
        logger.debug(f"Agent '{self.name}' built {len(messages)} messages for conversation")
        
        # Get response from SimpleAI
        logger.debug(f"Agent '{self.name}' calling SimpleAI chat with tools={'enabled' if self.tool_schemas else 'disabled'}")
        response = SimpleAI.chat(
            messages=messages,
            tools=self.tool_schemas if self.tool_schemas else None,
            stream=stream
        )
        
        # Handle tool calls if present
        if isinstance(response, dict) and "tool_calls" in response:
            tool_results = self._execute_tools(response["tool_calls"])
            
            # Add tool results to conversation and get final response
            messages.append({
                "role": "assistant",
                "content": response.get("content", ""),
                "tool_calls": response["tool_calls"]
            })
            
            # Add tool results - handle different formats for different providers
            config = SimpleAI.get_config()
            if config and config.provider == "claude":
                # Claude expects tool results in a different format
                tool_results_content = []
                for tool_call, result in tool_results:
                    tool_results_content.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call["id"],
                        "content": str(result)
                    })
                
                # Add tool results as user message for Claude
                if tool_results_content:
                    messages.append({
                        "role": "user",
                        "content": tool_results_content
                    })
            else:
                # OpenAI format with tool role
                for tool_call, result in tool_results:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": str(result)
                    })
            
            # Get final response
            logger.debug(f"Agent '{self.name}' getting final response after tool execution")
            final_response = SimpleAI.chat(messages=messages, stream=stream)
            
            # Store in memory if enabled
            if self.use_memory:
                logger.debug(f"Agent '{self.name}' storing {len(tool_results)} tool results in memory")
                for tool_call, result in tool_results:
                    # Handle both old and new tool call formats
                    if "function" in tool_call:
                        tool_name = tool_call["function"]["name"]
                    else:
                        tool_name = tool_call["name"]
                    self.memory.append((tool_name, result))
                    logger.debug(f"Agent '{self.name}' stored tool result: {tool_name} -> {str(result)[:100]}{'...' if len(str(result)) > 100 else ''}")
            
            logger.debug(f"Agent '{self.name}' returning final response: {final_response[:100]}{'...' if len(final_response) > 100 else ''}")
            return final_response
        
        logger.debug(f"Agent '{self.name}' returning direct response (no tools): {response[:100]}{'...' if len(response) > 100 else ''}")
        return response
    
    async def achat(self, message: str, stream: bool = False) -> str:
        """
        Async version of chat.
        
        Args:
            message: User message
            stream: Enable streaming response
            
        Returns:
            Agent response
        """
        # Build conversation messages
        messages = self._build_messages(message)
        
        # Get response from SimpleAI
        response = await SimpleAI.achat(
            messages=messages,
            tools=self.tool_schemas if self.tool_schemas else None,
            stream=stream
        )
        
        # Handle tool calls if present
        if isinstance(response, dict) and "tool_calls" in response:
            tool_results = self._execute_tools(response["tool_calls"])
            
            # Add tool results to conversation and get final response
            messages.append({
                "role": "assistant",
                "content": response.get("content", ""),
                "tool_calls": response["tool_calls"]
            })
            
            # Add tool results - handle different formats for different providers
            config = SimpleAI.get_config()
            if config and config.provider == "claude":
                # Claude expects tool results in a different format
                tool_results_content = []
                for tool_call, result in tool_results:
                    tool_results_content.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call["id"],
                        "content": str(result)
                    })
                
                # Add tool results as user message for Claude
                if tool_results_content:
                    messages.append({
                        "role": "user",
                        "content": tool_results_content
                    })
            else:
                # OpenAI format with tool role
                for tool_call, result in tool_results:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": str(result)
                    })
            
            # Get final response
            final_response = await SimpleAI.achat(messages=messages, stream=stream)
            
            # Store in memory if enabled
            if self.use_memory:
                for tool_call, result in tool_results:
                    # Handle both old and new tool call formats
                    if "function" in tool_call:
                        tool_name = tool_call["function"]["name"]
                    else:
                        tool_name = tool_call["name"]
                    self.memory.append((tool_name, result))
            
            return final_response
        
        return response
    
    def _build_messages(self, user_message: str) -> List[Dict[str, Any]]:
        """Build conversation messages including system prompt and memory."""
        messages = []
        
        # Add system prompt
        messages.append({
            "role": "system",
            "content": self.system_prompt
        })
        
        # Add memory context if available
        if self.use_memory and self.memory:
            memory_context = "Previous tool results:\n"
            for tool_name, result in self.memory:
                memory_context += f"- {tool_name}: {result}\n"
            
            messages.append({
                "role": "system",
                "content": memory_context
            })
        
        # Add user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    def _execute_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], Any]]:
        """Execute tool calls and return results."""
        logger.debug(f"Agent '{self.name}' executing {len(tool_calls)} tool calls")
        results = []
        
        for i, tool_call in enumerate(tool_calls, 1):
            # Handle both old and new tool call formats
            if "function" in tool_call:
                # New format: {"id": "...", "type": "function", "function": {"name": "...", "arguments": "..."}}
                tool_name = tool_call["function"]["name"]
                arguments = tool_call["function"]["arguments"]
            else:
                # Old format: {"id": "...", "name": "...", "arguments": "..."}
                tool_name = tool_call["name"]
                arguments = tool_call["arguments"]
            
            logger.debug(f"Agent '{self.name}' tool call {i}/{len(tool_calls)}: {tool_name} with args: {arguments}")
            
            if tool_name not in self.tool_map:
                error_msg = f"Unknown tool: {tool_name}"
                logger.error(f"Agent '{self.name}' error: {error_msg}")
                results.append((tool_call, error_msg))
                continue
            
            try:
                # Parse arguments
                if isinstance(arguments, str):
                    args = json.loads(arguments)
                else:
                    args = arguments
                
                logger.debug(f"Agent '{self.name}' executing tool '{tool_name}' with parsed args: {args}")
                
                # Execute tool
                tool_func = self.tool_map[tool_name]
                result = tool_func(**args)
                results.append((tool_call, result))
                
                logger.debug(f"Agent '{self.name}' tool '{tool_name}' returned: {str(result)[:200]}{'...' if len(str(result)) > 200 else ''}")
                
            except json.JSONDecodeError as e:
                error_msg = f"Invalid tool arguments: {e}"
                logger.error(f"Agent '{self.name}' JSON error: {error_msg}")
                results.append((tool_call, error_msg))
            except Exception as e:
                error_msg = f"Tool execution failed: {e}"
                logger.error(f"Agent '{self.name}' tool error: {error_msg}")
                results.append((tool_call, error_msg))
        
        return results
    
    def clear_memory(self) -> None:
        """Clear agent memory."""
        self.memory.clear()
        logger.debug(f"Agent '{self.name}' memory cleared")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "entries": len(self.memory),
            "max_entries": self.memory.maxlen,
            "tools_used": list(set(tool for tool, _ in self.memory))
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return f"SimpleAgent(name='{self.name}', tools={len(self.tools)}, memory={self.use_memory})"