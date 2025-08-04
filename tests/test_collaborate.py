"""
Tests for SimpleCollaborate multi-agent coordination.
"""

import pytest
from unittest.mock import Mock, patch
from core import SimpleAgent, SimpleTool, SimpleCollaborate
from core.exceptions import ConfigurationError


# Test tools for agents
@SimpleTool("Analyze text")
def analyze_text(text: str) -> str:
    """Analyze the given text."""
    return f"Analysis: {text} contains {len(text.split())} words"


@SimpleTool("Generate summary")
def generate_summary(content: str) -> str:
    """Generate a summary of content."""
    return f"Summary: {content[:50]}..."


@SimpleTool("Review content")
def review_content(text: str) -> str:
    """Review and improve content."""
    return f"Reviewed: {text} [improved]"


class TestSimpleCollaborate:
    """Test SimpleCollaborate functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        # Mock SimpleAI configuration
        with patch('simpleai.agent.SimpleAI.get_config') as mock_config:
            mock_config.return_value = Mock()
            
            # Create test agents
            self.analyst = SimpleAgent(
                system_prompt="You analyze data.",
                tools=[analyze_text],
                name="Analyst"
            )
            
            self.writer = SimpleAgent(
                system_prompt="You write content.",
                tools=[generate_summary],
                name="Writer"
            )
            
            self.editor = SimpleAgent(
                system_prompt="You edit content.",
                tools=[review_content],
                name="Editor"
            )
    
    def test_collaborate_initialization(self):
        """Test collaboration initialization."""
        with patch('simpleai.collaborate.SimpleAI.get_config') as mock_config:
            mock_config.return_value = Mock()
            
            collab = SimpleCollaborate([self.analyst, self.writer])
            
            assert len(collab.agents) == 2
            assert collab.shared_memory is True
            assert collab.agents[0].name == "Analyst"
            assert collab.agents[1].name == "Writer"
    
    def test_collaborate_without_config(self):
        """Test collaboration without SimpleAI configuration."""
        with patch('simpleai.collaborate.SimpleAI.get_config') as mock_config:
            mock_config.return_value = None
            
            with pytest.raises(ConfigurationError):
                SimpleCollaborate([self.analyst])
    
    def test_collaborate_no_agents(self):
        """Test collaboration with no agents."""
        with patch('simpleai.collaborate.SimpleAI.get_config') as mock_config:
            mock_config.return_value = Mock()
            
            with pytest.raises(ValueError) as exc_info:
                SimpleCollaborate([])
            assert "At least one agent" in str(exc_info.value)
    
    def test_collaborate_auto_naming(self):
        """Test automatic agent naming."""
        with patch('simpleai.collaborate.SimpleAI.get_config') as mock_config:
            mock_config.return_value = Mock()
            
            # Create agents without names
            agent1 = SimpleAgent(system_prompt="Test 1")
            agent2 = SimpleAgent(system_prompt="Test 2")
            
            collab = SimpleCollaborate([agent1, agent2])
            
            assert collab.agents[0].name == "Agent1"
            assert collab.agents[1].name == "Agent2"
    
    @patch('simpleai.collaborate.SimpleAI.chat')
    def test_create_plan(self, mock_chat):
        """Test plan creation."""
        with patch('simpleai.collaborate.SimpleAI.get_config') as mock_config:
            mock_config.return_value = Mock()
            
            # Mock planning response
            mock_chat.return_value = '''[
                {
                    "step": 1,
                    "agent": "Analyst",
                    "action": "Analyze the data",
                    "instructions": "Look for patterns"
                },
                {
                    "step": 2,
                    "agent": "Writer",
                    "action": "Write a report",
                    "instructions": "Based on analysis"
                }
            ]'''
            
            collab = SimpleCollaborate([self.analyst, self.writer])
            plan = collab._create_plan("Analyze sales data")
            
            assert len(plan) == 2
            assert plan[0]["agent"] == "Analyst"
            assert plan[1]["agent"] == "Writer"
    
    @patch('simpleai.config.SimpleAI.chat')
    def test_execute_plan(self, mock_chat):
        """Test plan execution."""
        with patch('simpleai.collaborate.SimpleAI.get_config') as mock_config:
            mock_config.return_value = Mock()
            
            # Mock both planning and agent execution calls
            mock_chat.side_effect = [
                # First call - planning
                '''[
                    {
                        "step": 1,
                        "agent": "Analyst",
                        "action": "Analyze data",
                        "instructions": "Analyze the input"
                    }
                ]''',
                # Second call - agent execution
                "Analysis complete: found 3 trends"
            ]
            
            collab = SimpleCollaborate([self.analyst])
            result = collab.execute("Analyze Q4 data")
            
            assert result["task"] == "Analyze Q4 data"
            assert len(result["plan"]) == 1
            assert len(result["results"]) == 1
            assert result["results"][0]["status"] == "success"
            assert "Analysis complete" in result["results"][0]["output"]
    
    def test_shared_memory(self):
        """Test shared memory functionality."""
        with patch('simpleai.collaborate.SimpleAI.get_config') as mock_config:
            mock_config.return_value = Mock()
            
            collab = SimpleCollaborate(
                [self.analyst, self.writer],
                shared_memory=True,
                memory_size=5
            )
            
            # Add entries to shared memory
            collab.memory.append(("Analyst", "Result 1"))
            collab.memory.append(("Writer", "Result 2"))
            
            assert len(collab.memory) == 2
            assert collab.memory[0] == ("Analyst", "Result 1")
    
    def test_memory_stats(self):
        """Test memory statistics."""
        with patch('simpleai.collaborate.SimpleAI.get_config') as mock_config:
            mock_config.return_value = Mock()
            
            collab = SimpleCollaborate([self.analyst, self.writer])
            
            # Add memory entries
            collab.memory.append(("Analyst", "Result 1"))
            collab.memory.append(("Writer", "Result 2"))
            collab.memory.append(("Analyst", "Result 3"))
            
            stats = collab.get_memory_stats()
            
            assert stats["entries"] == 3
            assert stats["agent_contributions"]["Analyst"] == 2
            assert stats["agent_contributions"]["Writer"] == 1
    
    @patch('simpleai.collaborate.SimpleAI.chat')
    def test_plan_fallback(self, mock_chat):
        """Test plan creation fallback when parsing fails."""
        with patch('simpleai.collaborate.SimpleAI.get_config') as mock_config:
            mock_config.return_value = Mock()
            
            # Mock invalid planning response
            mock_chat.return_value = "Invalid JSON response"
            
            collab = SimpleCollaborate([self.analyst])
            plan = collab._create_plan("Test task")
            
            # Should fall back to simple sequential plan
            assert len(plan) == 1
            assert plan[0]["agent"] == "Analyst"
            assert plan[0]["step"] == 1