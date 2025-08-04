# SimpleAI - Powerful Simplicity for AI Agents

A lightweight, production-ready framework for building AI agents with tool capabilities. Enterprise-grade capabilities with the simplest possible API.

## 🚀 Features

- **Global Configuration**: Configure once, use everywhere
- **Multi-Provider Support**: Works with OpenAI and Claude
- **Agent Tools**: Easy tool creation with `@SimpleTool` decorator
- **Memory Management**: Built-in conversation memory for agents
- **Multi-Agent Collaboration**: Coordinate multiple agents with AI-powered planning
- **Async Support**: Full async/await support for high-performance applications
- **Type Safe**: Comprehensive type hints throughout
- **Production Ready**: Proper error handling, logging, and retries

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🎯 Quick Start

### Basic Chat

```python
from core import SimpleAI

# Configure once globally
SimpleAI.configure(
    api_key="your-api-key",  # or use env var OPENAI_API_KEY
    provider="openai",
    model="gpt-4o-mini"
)

# Chat directly
response = SimpleAI.chat("Hello! How are you?")
print(response)
```

### Agent with Tools

```python
from core import SimpleAI, SimpleAgent, SimpleTool


# Define a tool
@SimpleTool("Get weather information")
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny, 72°F"


# Create an agent
agent = SimpleAgent(
    system_prompt="You are a helpful weather assistant.",
    tools=[get_weather]
)

# Use the agent
response = agent.chat("What's the weather in New York?")
print(response)
```

### Multi-Agent Collaboration

```python
from core import SimpleAI, SimpleAgent, SimpleTool, SimpleCollaborate

# Create specialized agents
analyst = SimpleAgent(
    system_prompt="You analyze data and identify patterns.",
    tools=[analyze_data]
)

writer = SimpleAgent(
    system_prompt="You write clear, concise reports.",
    tools=[write_report]
)

# Create collaboration
team = SimpleCollaborate([analyst, writer])

# Execute collaborative task
result = team.execute("Analyze Q4 sales data and write executive summary")
```

## 🔧 Configuration

### Environment Variables

```bash
# OpenAI
export OPENAI_API_KEY="your-openai-key"

# Claude
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### Global Configuration

```python
SimpleAI.configure(
    api_key="...",           # Optional if env var is set
    provider="openai",       # or "claude"
    model="gpt-4o",         # Model name
    temperature=0.7,         # 0-2
    max_tokens=1000,        # Max response length
    timeout=30,             # Request timeout
    max_retries=3           # Retry attempts
)
```

## 📚 Advanced Usage

### Custom Tools with Type Hints

```python
@SimpleTool("Search product database")
def search_products(
    query: str,
    category: str = "all",
    max_results: int = 10
) -> list:
    # Tool implementation
    return [{"name": "Product 1", "price": 99.99}]
```

### Memory Management

```python
# Agent with memory
agent = SimpleAgent(
    system_prompt="You are a personal assistant.",
    use_memory=True,
    memory_size=50  # Keep last 50 interactions
)

# Check memory
stats = agent.get_memory_stats()
print(f"Memory entries: {stats['entries']}")

# Clear memory
agent.clear_memory()
```

### Async Operations

```python
import asyncio

async def main():
    # Async chat
    response = await SimpleAI.achat("Hello!")
    
    # Async agent
    agent = SimpleAgent(system_prompt="Assistant")
    response = await agent.achat("Help me with Python")
    
    # Async collaboration
    team = SimpleCollaborate([agent1, agent2])
    result = await team.aexecute("Complex task")

asyncio.run(main())
```

### Provider Switching

```python
# Start with OpenAI
SimpleAI.configure(provider="openai", model="gpt-4o")
response = SimpleAI.chat("Hello from OpenAI")

# Switch to Claude
SimpleAI.configure(provider="claude", model="claude-3-5-sonnet-20241022")
response = SimpleAI.chat("Hello from Claude")
```

## 🏗️ Architecture

```
simpleai/
├── config.py       # Global configuration management
├── agent.py        # SimpleAgent and SimpleTool
├── collaborate.py  # Multi-agent collaboration
├── exceptions.py   # Custom exceptions
└── utils.py        # Utility functions
```

### Design Principles

1. **Global Configuration**: No need to pass config objects around
2. **Simple API**: Get started with just 3 lines of code
3. **Provider Agnostic**: Same code works with different AI providers
4. **Production First**: Built for real applications, not demos

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=simpleai

# Run specific test file
pytest tests/test_agent.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔮 Roadmap

- [ ] Additional provider support (Gemini, Mistral, etc.)
- [ ] Built-in tool library (web search, calculations, etc.)
- [ ] Persistent agent memory with database backends
- [ ] Advanced planning strategies for collaboration
- [ ] Tool result caching and optimization
- [ ] Structured output support

## ❓ FAQ

**Q: Do I need to configure SimpleAI for each agent?**  
A: No! Configure once globally, and all agents use the same configuration automatically.

**Q: Can I use different models for different agents?**  
A: Currently, all agents use the global configuration. Model-specific agents are on the roadmap.

**Q: How do I handle rate limits?**  
A: SimpleAI includes automatic retries with exponential backoff for rate limit errors.

**Q: Can I use this in production?**  
A: Yes! SimpleAI is designed with production use in mind, including proper error handling, logging, and async support.

## 🆘 Support

- Check the [examples](examples/) directory for more usage patterns
- Review the test files for detailed API usage
- Open an issue for bugs or feature requests

---

**SimpleAI** - Because AI should be simple to use, powerful to deploy.