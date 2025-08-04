"""
Generate command - Create examples and project templates.
"""

from pathlib import Path
from typing import Dict, Any, List

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

from cli.utils import show_success_message
from cli.templates.generators import generate_agent_project, generate_collaboration_project

console = Console()


@click.group()
def generate():
    """
    Generate examples and project templates.
    
    Create ready-to-use examples that demonstrate different SimpleAI capabilities
    and patterns for building AI agents and collaborations.
    """
    pass


@generate.command()
@click.option(
    "--type",
    "example_types",
    multiple=True,
    help="Specific example types to generate (can be used multiple times)",
)
@click.option(
    "--all",
    "generate_all",
    is_flag=True,
    help="Generate all available examples",
)
@click.pass_context
def examples(ctx, example_types: tuple, generate_all: bool):
    """
    Generate example projects.
    
    Creates various example projects demonstrating different use cases
    and patterns for SimpleAI agents and collaborations.
    
    Available types:
      basic_agent, weather_bot, customer_service, data_analysis,
      content_creation, research_assistant, multi_agent_team
    
    Examples:
      simpleai generate examples --type basic_agent
      simpleai generate examples --type customer_service --type data_analysis
      simpleai generate examples --all
    """
    output_dir = ctx.obj["output_dir"]
    examples_dir = output_dir / "examples"
    
    # Define available examples
    available_examples = get_available_examples()
    
    if generate_all:
        selected_examples = list(available_examples.keys())
    elif example_types:
        selected_examples = []
        for ex_type in example_types:
            if ex_type in available_examples:
                selected_examples.append(ex_type)
            else:
                console.print(f"[yellow]Warning: Unknown example type '{ex_type}'[/yellow]")
        
        if not selected_examples:
            console.print("[red]No valid example types specified[/red]")
            show_available_examples(available_examples)
            return
    else:
        # Interactive selection
        selected_examples = interactive_example_selection(available_examples)
    
    if not selected_examples:
        console.print("[yellow]No examples selected[/yellow]")
        return
    
    # Generate selected examples
    generate_examples(selected_examples, available_examples, examples_dir)


@generate.command()
@click.argument("project_name")
@click.option(
    "--template",
    type=click.Choice(["basic_agent", "tool_agent", "collaboration", "research_team"]),
    default="basic_agent",
    help="Project template type",
)
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Interactive project setup",
)
@click.pass_context
def project(ctx, project_name: str, template: str, interactive: bool):
    """
    Generate a new project from template.
    
    Creates a complete project structure with all necessary files
    for starting a new SimpleAI project.
    
    Examples:
      simpleai generate project MyBot --template basic_agent
      simpleai generate project TeamWork --template collaboration
      simpleai generate project MyProject --interactive
    """
    output_dir = ctx.obj["output_dir"]
    projects_dir = output_dir / "projects"
    
    if interactive:
        generate_project_interactive(project_name, projects_dir)
    else:
        generate_project_from_template(project_name, template, projects_dir)


def get_available_examples() -> Dict[str, Dict[str, Any]]:
    """Get available example configurations."""
    
    return {
        "basic_agent": {
            "name": "Basic Agent",
            "description": "Simple single-agent with basic functionality",
            "complexity": "Beginner",
            "files": ["agent", "example", "readme"],
        },
        "weather_bot": {
            "name": "Weather Bot",
            "description": "Agent with weather tools and memory",
            "complexity": "Beginner",
            "files": ["agent", "tools", "example", "readme"],
        },
        "customer_service": {
            "name": "Customer Service Bot",
            "description": "Multi-tool agent for customer support",
            "complexity": "Intermediate",
            "files": ["agent", "tools", "knowledge_base", "example", "readme"],
        },
        "data_analysis": {
            "name": "Data Analysis Team",
            "description": "Collaboration for data analysis workflows",
            "complexity": "Intermediate", 
            "files": ["collaboration", "agents", "tools", "example", "readme"],
        },
        "content_creation": {
            "name": "Content Creation Team",
            "description": "Multi-agent content generation pipeline",
            "complexity": "Advanced",
            "files": ["collaboration", "agents", "tools", "templates", "example", "readme"],
        },
        "research_assistant": {
            "name": "Research Assistant",
            "description": "Comprehensive research and analysis agent",
            "complexity": "Intermediate",
            "files": ["agent", "tools", "knowledge", "example", "readme"],
        },
        "multi_agent_team": {
            "name": "Multi-Agent Team",
            "description": "Complex collaboration with specialized agents",
            "complexity": "Advanced",
            "files": ["collaboration", "agents", "coordination", "example", "readme"],
        },
    }


def show_available_examples(examples: Dict[str, Dict[str, Any]]):
    """Display available examples in a table."""
    
    table = Table(title="Available Examples", show_header=True, header_style="bold blue")
    table.add_column("Type", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Description", style="dim")
    table.add_column("Complexity", style="yellow")
    
    for ex_type, info in examples.items():
        table.add_row(
            ex_type,
            info["name"],
            info["description"],
            info["complexity"]
        )
    
    console.print(table)


def interactive_example_selection(examples: Dict[str, Dict[str, Any]]) -> List[str]:
    """Interactive example selection."""
    
    console.print("\n[bold blue]📚 Available Examples:[/bold blue]")
    show_available_examples(examples)
    
    console.print("\n[bold]Select examples to generate:[/bold]")
    console.print("Enter example types separated by commas, or 'all' for everything:")
    
    user_input = input("Examples: ").strip()
    
    if user_input.lower() == 'all':
        return list(examples.keys())
    
    selected = []
    for ex_type in user_input.split(','):
        ex_type = ex_type.strip()
        if ex_type in examples:
            selected.append(ex_type)
        else:
            console.print(f"[yellow]Unknown example: {ex_type}[/yellow]")
    
    return selected


def generate_examples(
    selected_examples: List[str],
    available_examples: Dict[str, Dict[str, Any]],
    examples_dir: Path,
):
    """Generate the selected examples."""
    
    console.print(f"\n[blue]🚀 Generating {len(selected_examples)} examples...[/blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        
        task = progress.add_task("Generating examples...", total=len(selected_examples))
        
        for example_type in selected_examples:
            example_info = available_examples[example_type]
            progress.update(task, description=f"📝 Generating {example_info['name']}...")
            
            try:
                generate_single_example(example_type, example_info, examples_dir)
                progress.advance(task)
            except Exception as e:
                console.print(f"[red]❌ Failed to generate {example_type}: {e}[/red]")
                progress.advance(task)
    
    show_success_message(
        "📚 Examples Generated",
        f"Generated {len(selected_examples)} example projects in {examples_dir}",
        [
            f"cd {examples_dir}  # Navigate to examples folder",
            "ls  # See all generated examples",
            "cd <example_name>  # Enter an example",
            "python example_usage.py  # Test the example",
            "simpleai run <agent_file.py> \"Hello!\"  # Run the agent directly"
        ]
    )


def generate_single_example(
    example_type: str,
    example_info: Dict[str, Any],
    examples_dir: Path,
):
    """Generate a single example project."""
    
    example_dir = examples_dir / example_type
    example_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate based on example type
    if example_type == "basic_agent":
        generate_basic_agent_example(example_dir)
    elif example_type == "weather_bot":
        generate_weather_bot_example(example_dir)
    elif example_type == "customer_service":
        generate_customer_service_example(example_dir)
    elif example_type == "data_analysis":
        generate_data_analysis_example(example_dir)
    elif example_type == "content_creation":
        generate_content_creation_example(example_dir)
    elif example_type == "research_assistant":
        generate_research_assistant_example(example_dir)
    elif example_type == "multi_agent_team":
        generate_multi_agent_team_example(example_dir)
    else:
        raise ValueError(f"Unknown example type: {example_type}")


def generate_basic_agent_example(example_dir: Path):
    """Generate basic agent example."""
    
    agent_data = {
        "name": "BasicAgent",
        "system_prompt": "You are a helpful AI assistant that can answer questions and provide information.",
        "tools": [],
        "use_memory": True,
        "memory_size": 10,
    }
    
    generate_agent_project(agent_data, example_dir)


def generate_weather_bot_example(example_dir: Path):
    """Generate weather bot example."""
    
    agent_data = {
        "name": "WeatherBot",
        "system_prompt": "You are a helpful weather assistant. Use your tools to provide accurate weather information.",
        "tools": [
            {"name": "get_weather", "description": "Get current weather for a city"},
            {"name": "get_forecast", "description": "Get weather forecast for a city"},
        ],
        "use_memory": True,
        "memory_size": 20,
    }
    
    generate_agent_project(agent_data, example_dir)


def generate_customer_service_example(example_dir: Path):
    """Generate customer service example."""
    
    agent_data = {
        "name": "CustomerServiceBot",
        "system_prompt": "You are a professional customer service representative. Be helpful, polite, and solution-focused.",
        "tools": [
            {"name": "search_knowledge_base", "description": "Search the knowledge base for information"},
            {"name": "create_ticket", "description": "Create a support ticket"},
            {"name": "escalate_to_human", "description": "Escalate to human agent"},
        ],
        "use_memory": True,
        "memory_size": 30,
    }
    
    generate_agent_project(agent_data, example_dir)


def generate_data_analysis_example(example_dir: Path):
    """Generate data analysis collaboration example."""
    
    collab_data = {
        "name": "DataAnalysisTeam",
        "agents": ["DataAnalyst", "Visualizer", "ReportWriter"],
        "shared_memory": True,
        "memory_size": 50,
        "execution_type": "sequential",
    }
    
    generate_collaboration_project(collab_data, example_dir)


def generate_content_creation_example(example_dir: Path):
    """Generate content creation team example."""
    
    collab_data = {
        "name": "ContentCreationTeam", 
        "agents": ["Researcher", "Writer", "Editor", "SEOSpecialist"],
        "shared_memory": True,
        "memory_size": 75,
        "execution_type": "sequential",
    }
    
    generate_collaboration_project(collab_data, example_dir)


def generate_research_assistant_example(example_dir: Path):
    """Generate research assistant example."""
    
    agent_data = {
        "name": "ResearchAssistant",
        "system_prompt": "You are a comprehensive research assistant. Gather information, analyze it, and provide detailed insights.",
        "tools": [
            {"name": "web_search", "description": "Search the web for information"},
            {"name": "analyze_data", "description": "Analyze data and identify patterns"},
            {"name": "summarize_content", "description": "Summarize long content"},
            {"name": "fact_check", "description": "Verify facts and claims"},
        ],
        "use_memory": True,
        "memory_size": 40,
    }
    
    generate_agent_project(agent_data, example_dir)


def generate_multi_agent_team_example(example_dir: Path):
    """Generate multi-agent team example."""
    
    collab_data = {
        "name": "MultiAgentTeam",
        "agents": ["ProjectManager", "Researcher", "Analyst", "Developer", "Tester", "Reporter"],
        "shared_memory": True,
        "memory_size": 100,
        "execution_type": "hierarchical",
    }
    
    generate_collaboration_project(collab_data, example_dir)


def generate_project_from_template(project_name: str, template: str, projects_dir: Path):
    """Generate a project from a template."""
    
    project_dir = projects_dir / project_name
    
    if template == "basic_agent":
        agent_data = {
            "name": project_name,
            "system_prompt": f"You are {project_name}, a helpful AI assistant.",
            "tools": [],
            "use_memory": True,
            "memory_size": 20,
        }
        generate_agent_project(agent_data, project_dir)
        
    elif template == "tool_agent":
        agent_data = {
            "name": project_name,
            "system_prompt": f"You are {project_name}, an AI assistant with specialized tools.",
            "tools": [
                {"name": "example_tool", "description": "Example tool for demonstration"},
            ],
            "use_memory": True,
            "memory_size": 20,
        }
        generate_agent_project(agent_data, project_dir)
        
    elif template == "collaboration":
        collab_data = {
            "name": project_name,
            "agents": ["Agent1", "Agent2"],
            "shared_memory": True,
            "memory_size": 50,
            "execution_type": "sequential",
        }
        generate_collaboration_project(collab_data, project_dir)
        
    elif template == "research_team":
        collab_data = {
            "name": project_name,
            "agents": ["Researcher", "Analyst", "Writer"],
            "shared_memory": True,
            "memory_size": 75,
            "execution_type": "sequential",
        }
        generate_collaboration_project(collab_data, project_dir)
    
    show_success_message(
        f"🏗️ Project Created: {project_name}",
        f"Your new project is ready! Generated from {template} template in {project_dir}",
        [
            f"cd {project_dir}  # Navigate to your project",
            "python example_usage.py  # Test your project",
            "Edit the agent files to customize behavior",
            f"simpleai run *.py \"Your message here\"  # Run your project"
        ]
    )


def generate_project_interactive(project_name: str, projects_dir: Path):
    """Generate a project interactively."""
    
    console.print(f"\n[bold blue]🏗️  Interactive Project Creation: {project_name}[/bold blue]")
    
    # Choose project type
    project_types = {
        "1": ("Single Agent", "basic_agent"),
        "2": ("Agent with Tools", "tool_agent"), 
        "3": ("Multi-Agent Collaboration", "collaboration"),
        "4": ("Research Team", "research_team"),
    }
    
    console.print("\nSelect project type:")
    for key, (name, template) in project_types.items():
        console.print(f"  {key}. {name}")
    
    choice = input("Choice (1-4): ").strip()
    
    if choice in project_types:
        _, template = project_types[choice]
        generate_project_from_template(project_name, template, projects_dir)
    else:
        console.print("[red]Invalid choice[/red]")
        return