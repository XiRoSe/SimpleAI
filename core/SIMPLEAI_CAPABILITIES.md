# SimpleAI Framework - Capabilities and Architecture

## Overview
SimpleAI is a sophisticated, production-ready AI agent framework that combines enterprise-grade capabilities with an extremely simple API. It supports multiple AI providers (OpenAI, Claude), sophisticated tool systems, memory management, and multi-agent collaboration with AI-powered planning.

## Core Components

### 1. SimpleAI (Global Configuration)
- **Multi-Provider Support**: OpenAI, Claude (Anthropic), with automatic API handling
- **Global Configuration**: Set once, use everywhere
- **Direct Chat Interface**: `SimpleAI.chat()` and `SimpleAI.achat()` for direct AI interactions
- **Robust Error Handling**: Automatic retries, timeout management, provider fallbacks
- **Environment Integration**: Automatic .env file loading, environment variable support

### 2. SimpleAgent (Individual AI Agents)
**Core Features:**
- **Tool Integration**: Sophisticated tool system with automatic schema generation
- **Memory Management**: Configurable conversation memory with size limits
- **Multi-Provider**: Automatically uses global SimpleAI configuration
- **Async Support**: Full async/await support with `achat()`
- **Error Handling**: Robust tool execution error handling and recovery

**Key Capabilities:**
- Automatic tool schema generation from function signatures
- Memory persistence across conversations
- Tool result caching and context sharing
- Provider-specific optimization (OpenAI vs Claude tool formats)

### 3. SimpleTool (Tool Decorator System)
**Advanced Features:**
- **Automatic Schema Generation**: Extracts function signatures and creates JSON schemas
- **Type Support**: Full support for int, float, bool, list, dict, complex typing annotations
- **Parameter Validation**: Runtime parameter validation and type checking
- **Error Handling**: Graceful tool execution failure handling
- **Documentation Integration**: Uses docstrings and descriptions automatically

**Supported Types:**
- Basic types: `str`, `int`, `float`, `bool`
- Collections: `list`, `dict`, `List[int]`, `List[str]`, etc.
- Optional parameters with defaults
- Required vs optional parameter detection

### 4. SimpleCollaborate (Multi-Agent Orchestration)
**Advanced Capabilities:**
- **AI-Powered Planning**: Uses AI to analyze tasks and create execution plans
- **Agent Coordination**: Automatically coordinates multiple agents based on their capabilities
- **Shared Memory**: Agents can share context and build upon each other's work
- **Parallel Execution**: Support for parallel agent execution (async)
- **Dynamic Planning**: Can adapt plans based on agent capabilities and tools

**Planning Intelligence:**
- Analyzes agent system prompts and available tools
- Creates step-by-step execution plans
- Handles agent name validation and correction
- Provides fallback planning when AI planning fails
- Context passing between execution steps

## Framework Philosophy

### Enterprise-Grade Features
1. **Reliability**: Automatic retries, timeout handling, graceful degradation
2. **Observability**: Comprehensive logging, memory statistics, execution tracking
3. **Scalability**: Async support, parallel execution, memory management
4. **Flexibility**: Multi-provider support, configurable behavior, extensible tool system

### Simple API Design
- **One-Line Configuration**: `SimpleAI.configure(provider="openai", model="gpt-4o")`
- **Minimal Agent Creation**: `agent = SimpleAgent(system_prompt="...", tools=[...])`
- **Natural Tool Creation**: `@SimpleTool("description") def my_tool(param: str): ...`
- **Easy Collaboration**: `collab = SimpleCollaborate([agent1, agent2])`

## Best Practices for Implementations

### 1. Tool Design
```python
@SimpleTool("Generate marketing copy for specific platforms and audiences")
def generate_marketing_copy(
    platform: str,
    audience: str, 
    key_message: str,
    tone: str = "professional",
    word_count: int = 100
) -> str:
    # Actual implementation logic here
    # Should be specific to the use case
    pass
```

### 2. Agent Specialization
- Create agents with specific, focused system prompts
- Provide relevant tools that match the agent's role
- Use descriptive names that reflect the agent's purpose
- Enable memory for conversational agents, disable for stateless ones

### 3. Multi-Agent Design
- Design agents with complementary capabilities
- Use shared memory when agents need to build on each other's work
- Create clear, specific system prompts that define each agent's role
- Provide tools that are relevant to each agent's specific function

### 4. Memory Management
- Use memory for conversational workflows
- Set appropriate memory sizes (20 for agents, 50+ for collaborations)
- Clear memory when switching contexts or starting new sessions
- Monitor memory usage with `get_memory_stats()`

## Implementation Patterns

### Single-Purpose Agents
Perfect for focused tasks like content generation, data analysis, or specific domain expertise.

### Multi-Agent Collaborations
Ideal for complex workflows requiring different specializations working together.

### Tool-Heavy Agents
For agents that need to interact with external systems, APIs, databases, or perform computations.

### Conversational Agents
For chat-like interfaces that need to maintain context and remember previous interactions.

## Code Generation Guidelines

When generating implementations:

1. **Analyze the Task**: Understand what the user wants to accomplish
2. **Choose Architecture**: Single agent vs collaboration based on complexity
3. **Design Tools**: Create specific, useful tools for the task domain
4. **Write System Prompts**: Craft detailed, specific prompts that guide behavior
5. **Configure Memory**: Set appropriate memory settings for the use case
6. **Add Error Handling**: Include proper exception handling and validation
7. **Provide Examples**: Include meaningful example usage and testing

## Domain-Specific Considerations

### Marketing/Content Creation
- Tools for content generation, grammar checking, platform optimization
- Agents specialized for different content types or platforms
- Memory for maintaining brand voice and style consistency

### Data Analysis
- Tools for data processing, visualization, statistical analysis
- Agents specialized for different analysis types
- Collaboration for multi-step analysis workflows

### Customer Service
- Tools for knowledge base access, ticket management, escalation
- Memory for conversation context and customer history
- Multi-agent for complex issue resolution

### Research and Development
- Tools for information gathering, synthesis, report generation
- Collaboration for multi-perspective analysis
- Memory for building comprehensive research context

This framework is designed to be both powerful and accessible, enabling sophisticated AI applications with minimal boilerplate code while maintaining enterprise-grade reliability and performance.