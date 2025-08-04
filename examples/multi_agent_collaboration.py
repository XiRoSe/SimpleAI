"""
Example of multi-agent collaboration using SimpleCollaborate.
"""

from core import SimpleAI, SimpleAgent, SimpleTool, SimpleCollaborate


# Define tools for different agents
@SimpleTool("Analyze data and identify patterns")
def analyze_data(data: str) -> str:
    """Analyze data and identify patterns."""
    return f"Analysis of '{data}': Found 3 key patterns - trend A (increasing), trend B (cyclic), trend C (stable)"


@SimpleTool("Generate visualizations")
def create_visualization(data_type: str) -> str:
    """Create visualization for data."""
    return f"Created {data_type} visualization: [Chart showing data trends and patterns]"


@SimpleTool("Write report sections")
def write_section(topic: str, content: str) -> str:
    """Write a report section."""
    return f"# {topic}\n\n{content}\n\nThis section provides detailed analysis of {topic.lower()}."


@SimpleTool("Review and edit text")
def review_content(content: str) -> str:
    """Review and edit content for clarity."""
    return f"Reviewed content: {content}\n[Edits: Improved clarity, fixed grammar, added professional tone]"


@SimpleTool("Research additional information")
def research_topic(topic: str) -> str:
    """Research additional information about a topic."""
    return f"Research on '{topic}': Found 5 relevant sources with key insights about current trends and best practices."


def data_analysis_team_example():
    """Example of a data analysis team working together."""
    print("=== Data Analysis Team Example ===")
    
    # Configure SimpleAI
    SimpleAI.configure(
        provider="openai",
        model="gpt-4o-mini"
    )
    
    # Create specialized agents
    analyst = SimpleAgent(
        system_prompt="You are a data analyst. Analyze data, identify patterns, and provide insights.",
        tools=[analyze_data, create_visualization],
        name="DataAnalyst"
    )
    
    writer = SimpleAgent(
        system_prompt="You are a technical writer. Create clear, professional reports based on analysis.",
        tools=[write_section],
        name="ReportWriter"
    )
    
    editor = SimpleAgent(
        system_prompt="You are an editor. Review content for clarity, accuracy, and professionalism.",
        tools=[review_content],
        name="Editor"
    )
    
    # Create collaboration
    team = SimpleCollaborate(
        agents=[analyst, writer, editor],
        shared_memory=True
    )
    
    # Execute collaborative task
    result = team.execute(
        "Analyze Q4 sales data and create a professional report with visualizations"
    )
    
    print("Execution Plan:")
    for step in result['plan']:
        print(f"  Step {step['step']}: {step['agent']} - {step['action']}")
    
    print("\nResults:")
    for res in result['results']:
        print(f"\n{res['agent']} (Step {res['step']}):")
        print(f"Status: {res['status']}")
        print(f"Output: {res['output'][:200]}...")


def research_team_example():
    """Example of a research team collaboration."""
    print("\n=== Research Team Example ===")
    
    SimpleAI.configure(provider="openai")
    
    # Create research team
    researcher = SimpleAgent(
        system_prompt="You are a researcher. Find and analyze information on topics.",
        tools=[research_topic],
        name="Researcher"
    )
    
    analyst = SimpleAgent(
        system_prompt="You are an analyst. Synthesize research findings into actionable insights.",
        tools=[analyze_data],
        name="Analyst"
    )
    
    writer = SimpleAgent(
        system_prompt="You are a content writer. Transform insights into engaging content.",
        tools=[write_section],
        name="Writer"
    )
    
    # Create collaboration
    research_team = SimpleCollaborate(
        agents=[researcher, analyst, writer],
        shared_memory=True,
        memory_size=100  # Larger memory for research
    )
    
    # Execute research project
    result = research_team.execute(
        "Research the impact of AI on healthcare, analyze the findings, and create a comprehensive report"
    )
    
    # Show memory usage
    memory_stats = research_team.get_memory_stats()
    print(f"\nMemory Stats: {memory_stats}")


def custom_planning_example():
    """Example with custom planning prompt."""
    print("\n=== Custom Planning Example ===")
    
    SimpleAI.configure(provider="claude")
    
    # Create agents
    agent1 = SimpleAgent(
        system_prompt="You are a creative strategist.",
        tools=[research_topic]
    )
    
    agent2 = SimpleAgent(
        system_prompt="You are an implementation specialist.",
        tools=[write_section]
    )
    
    # Custom planning prompt
    custom_prompt = """Create a blog plan for an hike in Japan. 
    Focus on creative solutions and practical implementation.
    Each step should build on the previous one.
    Format as JSON array with step, agent, action, and instructions."""
    
    team = SimpleCollaborate([agent1, agent2])
    
    result = team.execute(
        "Develop a social media strategy for a new product launch",
        planning_prompt=custom_prompt
    )
    
    print(f"Custom Plan Executed Successfully with result: {result}")


async def async_collaboration_example():
    """Example of async collaboration."""

    print("\n=== Async Collaboration Example ===")
    
    SimpleAI.configure(provider="openai")
    
    # Create simple agents
    agents = [
        SimpleAgent(
            system_prompt=f"You are assistant {i+1}. Provide insights on the given topic.",
            tools=[research_topic] if i == 0 else [write_section],
            name=f"Assistant{i+1}"
        )
        for i in range(3)
    ]
    
    # Create collaboration
    team = SimpleCollaborate(agents)
    
    # Execute asynchronously
    result = await team.aexecute(
        "Create a guide on best practices for remote work"
    )
    
    print("Async execution completed")
    print(f"Total steps: {len(result['results'])}")


if __name__ == "__main__":
    # Run examples
    # data_analysis_team_example()
    # research_team_example()
    custom_planning_example()
    
    # Run async example
    # import asyncio
    # asyncio.run(async_collaboration_example())