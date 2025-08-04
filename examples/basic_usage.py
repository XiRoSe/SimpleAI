"""
Basic usage examples for SimpleAI.
"""

from core import SimpleAI


def basic_chat_example():
    """Simple chat example."""
    print("=== Basic Chat Example ===")
    
    # Configure SimpleAI globally
    SimpleAI.configure(
        provider="openai",
        model="gpt-4o-mini",
        temperature=0.7
    )
    
    # Simple chat
    response = SimpleAI.chat("Hello! How are you today?")
    print(f"Response: {response}\n")
    
    # Chat with message history
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"}
    ]
    response = SimpleAI.chat(messages)
    print(f"Response with history: {response}\n")


def provider_switching_example():
    """Example of switching between providers."""
    print("=== Provider Switching Example ===")
    
    # Configure for OpenAI
    SimpleAI.configure(
        provider="openai",
        model="gpt-4o"
    )
    
    response = SimpleAI.chat("Tell me a joke")
    print(f"OpenAI response: {response}\n")
    
    # Switch to Claude
    SimpleAI.configure(
        provider="claude",
        model="claude-3-5-sonnet-20241022"
    )
    
    response = SimpleAI.chat("Tell me a different joke")
    print(f"Claude response: {response}\n")


def streaming_example():
    """Example of streaming responses."""
    print("=== Streaming Example ===")
    
    SimpleAI.configure(provider="openai")
    
    # Get streaming response
    stream = SimpleAI.chat("Write a short story about a robot", stream=True)
    
    print("Streaming response: ", end="")
    for chunk in stream:
        print(chunk, end="", flush=True)
    print("\n")


async def async_example():
    """Example of async chat."""

    print("=== Async Example ===")
    
    SimpleAI.configure(provider="openai")
    
    # Async chat
    response = await SimpleAI.achat("What are the benefits of async programming?")
    print(f"Async response: {response}\n")


if __name__ == "__main__":
    # Run examples
    basic_chat_example()
    # provider_switching_example()
    # streaming_example()
    
    # Run async example
    # import asyncio
    # asyncio.run(async_example())