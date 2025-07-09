# SimpleAI - Professional OpenAI Integration

A clean, modular, and production-ready Python library for OpenAI ChatGPT and Vision APIs.

## 🚀 Features

- **Modular Architecture**: Clean separation of concerns across 5 focused modules
- **Memory Management**: Configurable conversation history with token tracking
- **Vision Support**: Complete image analysis and OCR capabilities  
- **Retry Logic**: Robust error handling with configurable retry attempts
- **Type Safety**: Full type hints throughout
- **Production Ready**: Comprehensive logging, validation, and error handling

## 📁 Project Structure

```
SimpleAI/
├── configs.py              # Configuration classes
├── LocalChatMemory.py       # Memory management
├── OpenAIInfra.py          # Core infrastructure
├── ChatGPT.py              # Enhanced chat interface
├── VisionGPT.py            # Vision analysis capabilities
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## 🛠 Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd SimpleAI

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
echo "OPENAI_API_KEY=your-api-key-here" > .env

# Or set environment variable
export OPENAI_API_KEY="your-api-key-here"
```

## 📋 Requirements

```
openai>=1.0.0
requests>=2.25.0
python-dotenv>=0.19.0
```

## 🔧 Quick Start

### Basic Chat Usage

```python
from configs import ChatConfig
from ChatGPT import ChatGPT

# Configure the client (API key loaded automatically from .env)
config = ChatConfig(
    model="gpt-4o-mini",
    temperature=0.7,
    memory_size=20
)

# Start chatting
chat = ChatGPT(config)
response = chat.chat("Hello! How are you today?")
print(response)

# Continue the conversation (memory is maintained)
response = chat.chat("What did I just ask you?")
print(response)
```

### Vision Analysis

```python
from configs import VisionConfig
from VisionGPT import VisionGPT

# Configure for vision tasks (API key auto-loaded)
config = VisionConfig(detail="high")  # low, high, auto

# Analyze images
vision = VisionGPT(config)

# Analyze from URL
result = vision.analyze_image(
    "https://example.com/image.jpg", 
    "What objects do you see in this image?"
)

# Extract text (OCR)
text = vision.extract_text("https://example.com/document.jpg")

# Analyze local image
local_result = vision.analyze_local_image(
    "/path/to/image.jpg",
    "Describe this image in detail"
)
```

## 📚 Detailed Usage

### Configuration Options

```python
from configs import ChatConfig, VisionConfig

# Basic configuration (API key auto-loaded from .env)
basic_config = ChatConfig(
    model="gpt-4o-mini",        # Model to use
    temperature=0.9,            # Creativity (0-2)
    max_tokens=1000,           # Max response length
    top_p=1.0,                 # Nucleus sampling
    max_retries=3,             # Retry attempts
    memory_size=15             # Conversation history
)

# Or manually specify API key
manual_config = ChatConfig(
    api_key="your-specific-key",  # Override .env
    model="gpt-4o-mini"
)

# Vision-specific configuration
vision_config = VisionConfig(
    model="gpt-4o",            # Auto-set for vision
    detail="auto"              # Image detail level
)
```

### Memory Management

```python
from LocalChatMemory import ChatMemory

# Create memory instance
memory = ChatMemory(max_length=10)

# Add messages
memory.add_message("user", "Hello")
memory.add_message("assistant", "Hi there!")

# Get statistics
stats = memory.get_memory_stats()
print(f"Messages: {stats['message_count']}")
print(f"Estimated tokens: {stats['token_estimate']}")

# Export/clear
messages = memory.get_messages()
memory.clear()
```

### Advanced Chat Features

```python
from ChatGPT import ChatGPT

chat = ChatGPT(config)

# Different interaction modes
response = chat.ask("What is Python?")  # No memory
response = chat.complete("Write a poem about")  # Simple completion
response = chat.role_play("Shakespeare", "Hello")  # Character roleplay

# Utility functions
summary = chat.summarize(long_text, style="bullet")
translation = chat.translate("Hello", "Spanish")
explanation = chat.explain("Quantum Computing", level="simple")
ideas = chat.brainstorm("Marketing strategies", num_ideas=5)

# Code review
review = chat.review_code(your_code, language="python")

# Email generation
email = chat.write_email(
    purpose="Meeting request", 
    tone="professional", 
    length="short"
)

# Save/load conversations
chat.save_conversation("conversation.json")
chat.load_conversation("conversation.json")
```

### Vision Capabilities

```python
from VisionGPT import VisionGPT

vision = VisionGPT(config)

# Specialized analysis functions
scene = vision.describe_scene(image_url)
objects = vision.identify_objects(image_url)
document = vision.analyze_document(image_url)
chart_analysis = vision.analyze_chart_or_graph(image_url)
accessibility = vision.describe_for_accessibility(image_url)
artwork = vision.analyze_artwork(image_url)

# Compare images
comparison = vision.compare_images([url1, url2], "Find differences")

# Base64 image support
with open("image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()
    result = vision.send_vision_with_base64("Describe this", image_data)

# Validate URLs
validation = vision.validate_image_url(image_url)
print(validation)  # {"is_valid_url": True, "is_vision_compatible": True, ...}
```

### Core Infrastructure

```python
from OpenAIInfra import OpenAIInfra

# Direct infrastructure access
infra = OpenAIInfra(config)

# System prompts
response = infra.send_system_message(
    "You are a helpful assistant", 
    "What can you do?"
)

# Set persistent system prompt
infra.set_system_prompt("You are an expert Python developer")

# Export conversation
conversation = infra.export_conversation()

# Import conversation
infra.import_conversation(previous_messages)
```

## 🔒 Security Best Practices

### API Key Management

```python
import os
from configs import ChatConfig

# ✅ GOOD: Use environment variables
config = ChatConfig(api_key=os.getenv("OPENAI_API_KEY"))

# ❌ BAD: Never hardcode API keys
config = ChatConfig(api_key="sk-...")  # Don't do this!
```

### Environment Setup

```bash
# Linux/Mac
export OPENAI_API_KEY="your-key-here"

# Windows
set OPENAI_API_KEY=your-key-here

# Or use a .env file
echo "OPENAI_API_KEY=your-key-here" > .env
```

## 🎯 Use Cases

### Customer Support Bot

```python
config = ChatConfig(api_key=os.getenv("OPENAI_API_KEY"))
chat = ChatGPT(config)

chat.set_system_prompt("""
You are a helpful customer support representative.
Be polite, professional, and solution-focused.
""")

while True:
    user_input = input("Customer: ")
    if user_input.lower() == 'quit':
        break
    response = chat.chat(user_input)
    print(f"Support: {response}")
```

### Document Analysis Pipeline

```python
vision = VisionGPT(VisionConfig(api_key=os.getenv("OPENAI_API_KEY")))

def process_document(image_path):
    # Extract text
    text = vision.extract_text(image_path)
    
    # Analyze content
    analysis = vision.analyze_document(image_path)
    
    # Generate summary
    chat = ChatGPT(config)
    summary = chat.summarize(text, style="executive")
    
    return {
        "text": text,
        "analysis": analysis,
        "summary": summary
    }
```

## 🚨 Error Handling

```python
try:
    response = chat.send_message("Hello")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"API error: {e}")

# Check memory status
if chat.memory.is_full():
    print("Memory at capacity")
    chat.clear_memory()
```

## 📊 Monitoring & Logging

```python
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Monitor usage
stats = chat.get_memory_stats()
print(f"Current conversation: {stats['message_count']} messages")
print(f"Token estimate: {stats['token_estimate']}")
```

## 🔄 Migration from v1

If upgrading from the original single-file version:

```python
# Old way
from original_file import ChatGPT, ChatGPTVision

# New way
from configs import ChatConfig, VisionConfig
from ChatGPT import ChatGPT
from VisionGPT import VisionGPT

# Update initialization
config = ChatConfig(api_key="your-key")
chat = ChatGPT(config)
vision = VisionGPT(config)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Follow the existing code style
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details.

## 🆘 Support

- Check the documentation for common issues
- Review error messages for specific guidance
- Ensure your OpenAI API key has sufficient credits
- Verify image URLs are publicly accessible for vision tasks

## 🔮 Roadmap

- [ ] Async support with `AsyncOpenAI`
- [ ] Streaming responses
- [ ] Cost tracking and budgets
- [ ] Plugin system for custom tools
- [ ] Batch processing capabilities
- [ ] Advanced prompt templates

---

**Made with ❤️ for the SimpleAI community**