"""
Tests for SimpleAgent and SimpleTool.
"""

import pytest
from unittest.mock import Mock, patch
from core import SimpleAgent, SimpleTool
from core.exceptions import ConfigurationError, ToolError


# Test tools
@SimpleTool("Add two numbers")
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


@SimpleTool("Get user info")
def get_user_info(user_id: str, include_details: bool = False) -> dict:
    """Get user information."""
    return {
        "id": user_id,
        "name": "Test User",
        "details": {"age": 25} if include_details else None
    }


@SimpleTool("Failing tool", validate_params=True)
def failing_tool(required_param: str) -> str:
    """A tool that fails."""
    raise Exception("Tool failed!")


class TestSimpleTool:
    """Test SimpleTool decorator."""
    
    def test_tool_decoration(self):
        """Test that tool decorator adds metadata."""
        assert hasattr(add_numbers, 'is_tool')
        assert add_numbers.is_tool is True
        assert add_numbers.tool_name == "add_numbers"
        assert "Add two numbers" in add_numbers.tool_description
        assert add_numbers.tool_params is not None
    
    def test_tool_parameter_extraction(self):
        """Test parameter extraction from function signature."""
        params = add_numbers.tool_params
        assert params["type"] == "object"
        assert "a" in params["properties"]
        assert "b" in params["properties"]
        assert params["properties"]["a"]["type"] == "integer"
        assert params["properties"]["b"]["type"] == "integer"
        assert params["required"] == ["a", "b"]
    
    def test_tool_optional_params(self):
        """Test tool with optional parameters."""
        params = get_user_info.tool_params
        assert "user_id" in params["required"]
        assert "include_details" not in params["required"]
    
    def test_tool_execution(self):
        """Test tool execution."""
        result = add_numbers(a=5, b=3)
        assert result == 8
    
    def test_tool_error_handling(self):
        """Test tool error handling."""
        with pytest.raises(ToolError) as exc_info:
            failing_tool(required_param="test")
        assert "Tool execution failed" in str(exc_info.value)


class TestSimpleAgent:
    """Test SimpleAgent functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        # Mock SimpleAI configuration
        with patch('simpleai.agent.SimpleAI.get_config') as mock_config:
            mock_config.return_value = Mock()
            self.agent = SimpleAgent(
                system_prompt="You are a test assistant.",
                tools=[add_numbers, get_user_info],
                use_memory=True,
                memory_size=10,
                name="TestAgent"
            )
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        assert self.agent.system_prompt == "You are a test assistant."
        assert len(self.agent.tools) == 2
        assert self.agent.use_memory is True
        assert self.agent.name == "TestAgent"
        assert len(self.agent.tool_schemas) == 2
    
    def test_agent_without_config(self):
        """Test agent creation without SimpleAI configuration."""
        with patch('simpleai.agent.SimpleAI.get_config') as mock_config:
            mock_config.return_value = None
            
            with pytest.raises(ConfigurationError) as exc_info:
                SimpleAgent(system_prompt="Test")
            assert "SimpleAI not configured" in str(exc_info.value)
    
    def test_agent_tool_schemas(self):
        """Test tool schema generation."""
        schemas = self.agent.tool_schemas
        
        # Check first tool schema
        add_schema = next(s for s in schemas if s["function"]["name"] == "add_numbers")
        assert add_schema["type"] == "function"
        assert "Add two numbers" in add_schema["function"]["description"]
        assert add_schema["function"]["parameters"]["required"] == ["a", "b"]
    
    @patch('simpleai.agent.SimpleAI.chat')
    def test_agent_chat_no_tools(self, mock_chat):
        """Test agent chat without tool calls."""
        mock_chat.return_value = "Hello! How can I help?"
        
        response = self.agent.chat("Hello")
        
        assert response == "Hello! How can I help?"
        mock_chat.assert_called_once()
        
        # Check message building
        call_args = mock_chat.call_args
        messages = call_args.kwargs['messages']
        assert messages[0]['role'] == 'system'
        assert messages[0]['content'] == "You are a test assistant."
        assert messages[-1]['role'] == 'user'
        assert messages[-1]['content'] == "Hello"
    
    @patch('simpleai.agent.SimpleAI.chat')
    def test_agent_chat_with_tools(self, mock_chat):
        """Test agent chat with tool calls."""
        # First call returns tool request
        mock_chat.side_effect = [
            {
                "content": "I'll add those numbers for you.",
                "tool_calls": [{
                    "id": "call_123",
                    "name": "add_numbers",
                    "arguments": '{"a": 5, "b": 3}'
                }]
            },
            "The sum of 5 and 3 is 8."
        ]
        
        response = self.agent.chat("Add 5 and 3")
        
        assert response == "The sum of 5 and 3 is 8."
        assert mock_chat.call_count == 2
        
        # Check memory was updated
        assert len(self.agent.memory) == 1
        assert self.agent.memory[0] == ("add_numbers", 8)
    
    def test_agent_memory_management(self):
        """Test agent memory management."""
        # Add entries to memory
        for i in range(15):
            self.agent.memory.append((f"tool_{i}", f"result_{i}"))
        
        # Memory should only keep last 10 entries
        assert len(self.agent.memory) == 10
        assert self.agent.memory[0] == ("tool_5", "result_5")
        assert self.agent.memory[-1] == ("tool_14", "result_14")
    
    def test_agent_clear_memory(self):
        """Test clearing agent memory."""
        self.agent.memory.append(("test_tool", "test_result"))
        assert len(self.agent.memory) == 1
        
        self.agent.clear_memory()
        assert len(self.agent.memory) == 0
    
    def test_agent_memory_stats(self):
        """Test memory statistics."""
        self.agent.memory.append(("tool_a", "result_1"))
        self.agent.memory.append(("tool_b", "result_2"))
        self.agent.memory.append(("tool_a", "result_3"))
        
        stats = self.agent.get_memory_stats()
        assert stats["entries"] == 3
        assert stats["max_entries"] == 10
        assert "tool_a" in stats["tools_used"]
        assert "tool_b" in stats["tools_used"]
    
    def test_agent_without_memory(self):
        """Test agent without memory."""
        with patch('simpleai.agent.SimpleAI.get_config') as mock_config:
            mock_config.return_value = Mock()
            
            no_memory_agent = SimpleAgent(
                system_prompt="Test",
                use_memory=False
            )
            
            assert no_memory_agent.use_memory is False
            assert no_memory_agent.memory.maxlen == 0
    
    def test_agent_execute_tools(self):
        """Test tool execution."""
        tool_calls = [
            {
                "id": "call_1",
                "name": "add_numbers",
                "arguments": '{"a": 10, "b": 20}'
            },
            {
                "id": "call_2",
                "name": "get_user_info",
                "arguments": '{"user_id": "123", "include_details": true}'
            }
        ]
        
        results = self.agent._execute_tools(tool_calls)
        
        assert len(results) == 2
        assert results[0][1] == 30  # add_numbers result
        assert results[1][1]["id"] == "123"  # get_user_info result
        assert results[1][1]["details"] is not None
    
    def test_agent_unknown_tool(self):
        """Test handling of unknown tool."""
        tool_calls = [{
            "id": "call_1",
            "name": "unknown_tool",
            "arguments": '{}'
        }]
        
        results = self.agent._execute_tools(tool_calls)
        
        assert len(results) == 1
        assert "Unknown tool" in results[0][1]