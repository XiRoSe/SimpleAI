"""
Example of using SimpleAgent with tools.
"""

import random
from datetime import datetime
from typing import List
from core import SimpleAI, SimpleAgent, SimpleTool


# Define some tool functions
@SimpleTool("Get current weather for a city")
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    # Simulated weather data
    conditions = ["sunny", "cloudy", "rainy", "partly cloudy"]
    temp = random.randint(60, 85)
    return f"The weather in {city} is {random.choice(conditions)} with a temperature of {temp}°F"


@SimpleTool("Get current time in a timezone")
def get_time(timezone: str = "UTC") -> str:
    """Get the current time in a specific timezone."""
    # Simplified - just return current local time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Current time in {timezone}: {current_time}"


@SimpleTool("Calculate the sum of numbers")
def calculate_sum(numbers: List[float]) -> float:
    """Calculate the sum of a list of numbers."""
    return sum(numbers)


@SimpleTool("Search for information")
def search_info(query: str) -> str:
    """Search for information about a topic."""
    # Simulated search results
    return f"Here's what I found about '{query}': This is simulated search result content that would normally come from a real search API."


def weather_assistant_example():
    """Example of a weather assistant agent."""
    print("=== Weather Assistant Example ===")
    
    # Configure SimpleAI
    SimpleAI.configure(
        provider="openai",
        model="gpt-4o-mini"
    )
    
    # Create weather assistant agent
    weather_agent = SimpleAgent(
        system_prompt="You are a helpful weather assistant. Use the available tools to answer questions about weather and time.",
        tools=[get_weather, get_time],
        use_memory=True,
        name="WeatherBot"
    )
    
    # Ask about weather
    response = weather_agent.chat("What's the weather like in New York?")
    print(f"Response: {response}\n")
    
    # Ask about time
    response = weather_agent.chat("What time is it in London?")
    print(f"Response: {response}\n")
    
    # Ask a question that uses memory
    response = weather_agent.chat("Is it warmer in New York or should I check another city?")
    print(f"Response: {response}\n")
    
    # Check memory stats
    stats = weather_agent.get_memory_stats()
    print(f"Memory stats: {stats}\n")


def research_assistant_example():
    """Example of a research assistant with multiple tools."""
    print("=== Research Assistant Example ===")
    
    SimpleAI.configure(
        provider="openai",
        model="gpt-4o"
    )
    
    # Create research assistant
    research_agent = SimpleAgent(
        system_prompt="""You are a research assistant that helps users find and analyze information. 
        You have access to search and calculation tools. Always provide thorough, well-researched answers.""",
        tools=[search_info, calculate_sum, get_time],
        use_memory=True,
        name="ResearchBot"
    )
    
    # Complex query requiring multiple tools
    response = research_agent.chat(
        "Search for information about Python programming, then calculate the sum of [10, 20, 30, 40]"
    )
    print(f"Response: {response}\n")


def no_memory_agent_example():
    """Example of an agent without memory."""
    print("=== No Memory Agent Example ===")
    
    SimpleAI.configure(provider="openai")
    
    # Create agent without memory
    simple_agent = SimpleAgent(
        system_prompt="You are a simple calculator assistant.",
        tools=[calculate_sum],
        use_memory=False,  # No memory
        name="CalcBot"
    )
    
    # Each request is independent
    response1 = simple_agent.chat("Calculate the sum of [1, 2, 3]")
    print(f"First calculation: {response1}")
    
    response2 = simple_agent.chat("What did I just ask you to calculate?")
    print(f"Memory test: {response2}\n")


async def async_agent_example():
    """Example of async agent usage."""

    print("=== Async Agent Example ===")
    
    SimpleAI.configure(provider="openai")
    
    # Create agent
    agent = SimpleAgent(
        system_prompt="You are a helpful assistant with access to various tools.",
        tools=[get_weather, get_time, search_info]
    )
    
    # Async chat
    response = await agent.achat("What's the weather in Paris and what time is it there?")
    print(f"Async response: {response}\n")


if __name__ == "__main__":
    # Run examples
    weather_assistant_example()
    research_assistant_example()
    no_memory_agent_example()
    
    # Run async example
    # import asyncio
    # asyncio.run(async_agent_example())