"""
Utility functions for SimpleAI CLI.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text

from core import SimpleAI


console = Console()


def ensure_simpleai_configured():
    """Ensure SimpleAI is configured, prompt user if not."""
    
    try:
        # Try to get current config
        config = SimpleAI.get_config()
        if config:
            return  # Already configured
    except:
        pass
    
    # Not configured, prompt user
    console.print("[yellow]⚠️  SimpleAI not configured[/yellow]")
    
    # Check for API keys in environment
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_key and not anthropic_key:
        console.print("[red]No API keys found in environment variables[/red]")
        console.print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file")
        raise click.ClickException("API keys required")
    
    # Choose provider
    if openai_key and anthropic_key:
        provider = Prompt.ask(
            "Choose provider",
            choices=["openai", "claude"],
            default="openai"
        )
    elif openai_key:
        provider = "openai"
        console.print("Using OpenAI (found OPENAI_API_KEY)")
    else:
        provider = "claude"
        console.print("Using Claude (found ANTHROPIC_API_KEY)")
    
    # Choose model
    if provider == "openai":
        model = Prompt.ask(
            "Choose OpenAI model",
            choices=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
            default="gpt-4o-mini"
        )
    else:
        model = Prompt.ask(
            "Choose Claude model",
            choices=["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
            default="claude-3-5-sonnet-20241022"
        )
    
    # Configure SimpleAI
    try:
        SimpleAI.configure(provider=provider, model=model)
        console.print(f"[green]✅ SimpleAI configured with {provider} ({model})[/green]")
    except Exception as e:
        console.print(f"[red]❌ Configuration failed: {e}[/red]")
        raise click.ClickException("Failed to configure SimpleAI")


def save_yaml_file(data: Dict[str, Any], file_path: Path) -> None:
    """Save data to a YAML file."""
    
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, indent=2, sort_keys=False)


def load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """Load data from a YAML file."""
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_json_file(data: Dict[str, Any], file_path: Path) -> None:
    """Save data to a JSON file."""
    
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load data from a JSON file."""
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_timestamped_dir(base_dir: Path, prefix: str = "") -> Path:
    """Create a directory with timestamp."""
    
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    dir_name = f"{prefix}{timestamp}" if prefix else timestamp
    
    output_dir = base_dir / dir_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return output_dir


def validate_python_identifier(name: str) -> bool:
    """Check if a string is a valid Python identifier."""
    
    return name.isidentifier() and not name.startswith('_')


def format_python_name(name: str) -> str:
    """Format a name to be a valid Python identifier."""
    
    # Replace spaces and special characters with underscores
    import re
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    
    # Ensure it starts with a letter
    if not name[0].isalpha():
        name = f"agent_{name}"
    
    # Remove multiple underscores
    name = re.sub(r'_+', '_', name)
    
    # Remove trailing underscores
    name = name.strip('_')
    
    return name


def prompt_for_tools() -> List[Dict[str, str]]:
    """Interactive prompt for selecting/creating tools."""
    
    tools = []
    
    # Predefined common tools
    common_tools = {
        "web_search": "Search the web for information",
        "file_reader": "Read and analyze files",
        "data_analysis": "Analyze data and create insights",
        "text_processing": "Process and manipulate text",
        "email_sender": "Send emails",
        "api_caller": "Make API calls to external services",
        "calculator": "Perform mathematical calculations",
        "datetime_helper": "Handle date and time operations",
    }
    
    console.print("\n[bold blue]🔧 Tool Selection[/bold blue]")
    console.print("Choose from common tools or define custom ones:")
    
    # Show common tools
    for i, (tool_name, description) in enumerate(common_tools.items(), 1):
        console.print(f"  {i}. {tool_name} - {description}")
    
    console.print(f"  {len(common_tools) + 1}. Custom tool")
    console.print(f"  {len(common_tools) + 2}. Done")
    
    while True:
        choice = Prompt.ask(
            "\nSelect a tool",
            choices=[str(i) for i in range(1, len(common_tools) + 3)],
        )
        
        choice_num = int(choice)
        
        if choice_num <= len(common_tools):
            # Common tool selected
            tool_name = list(common_tools.keys())[choice_num - 1]
            description = common_tools[tool_name]
            tools.append({"name": tool_name, "description": description})
            console.print(f"[green]✅ Added {tool_name}[/green]")
            
        elif choice_num == len(common_tools) + 1:
            # Custom tool
            tool_name = Prompt.ask("Enter tool name")
            tool_name = format_python_name(tool_name)
            description = Prompt.ask("Enter tool description")
            tools.append({"name": tool_name, "description": description})
            console.print(f"[green]✅ Added custom tool {tool_name}[/green]")
            
        else:
            # Done
            break
        
        if not Confirm.ask("Add another tool?", default=False):
            break
    
    return tools


def show_success_message(title: str, message: str, next_steps: Optional[List[str]] = None):
    """Show a success message with optional next steps."""
    
    text = Text()
    text.append(f"✅ {message}\n", style="green")
    
    if next_steps:
        text.append("\n🚀 Next steps:\n", style="bold blue")
        for i, step in enumerate(next_steps, 1):
            text.append(f"   {i}. {step}\n", style="white")
    
    panel = Panel(text, title=title, border_style="green")
    console.print(panel)


def show_error_message(title: str, message: str, suggestions: Optional[List[str]] = None):
    """Show an error message with optional suggestions."""
    
    text = Text()
    text.append(f"❌ {message}\n", style="red")
    
    if suggestions:
        text.append("\n💡 Suggestions:\n", style="bold yellow")
        for i, suggestion in enumerate(suggestions, 1):
            text.append(f"   {i}. {suggestion}\n", style="white")
    
    panel = Panel(text, title=title, border_style="red")
    console.print(panel)


def get_file_template_vars(file_type: str) -> Dict[str, Any]:
    """Get template variables for different file types."""
    
    common_vars = {
        "timestamp": datetime.now().isoformat(),
        "cli_version": "1.0.0",
    }
    
    if file_type == "agent":
        return {
            **common_vars,
            "agent_name": "MyAgent",
            "system_prompt": "You are a helpful AI assistant.",
            "tools": [],
            "use_memory": True,
            "memory_size": 20,
        }
    
    elif file_type == "collaboration":
        return {
            **common_vars,
            "collaboration_name": "MyCollaboration",
            "agents": [],
            "shared_memory": True,
            "memory_size": 50,
        }
    
    return common_vars


def generate_project_name(task_description: str) -> str:
    """Generate a concise project name from task description using AI."""
    
    try:
        # Ensure SimpleAI is configured
        ensure_simpleai_configured()
        
        # Create prompt to generate project name
        prompt = f"""Generate a short, concise project name (2-3 words max) for this task:
        
Task: {task_description}

Requirements:
- Maximum 3 words
- Use snake_case format (lowercase with underscores)
- No spaces or special characters
- Descriptive but brief
- Professional and clean

Examples:
- "Create a weather bot" → "weather_bot"
- "Build a customer service system" → "customer_service"
- "Analyze sales data" → "sales_analysis"
- "Create a chatbot for restaurants" → "restaurant_bot"

Just return the project name, nothing else."""

        response = SimpleAI.chat(prompt, temperature=0.3)
        
        # Clean the response
        project_name = response.strip().lower()
        project_name = format_python_name(project_name)
        
        # Ensure it's not too long
        if len(project_name) > 30:
            project_name = project_name[:30].rstrip('_')
        
        return project_name
        
    except Exception:
        # Fallback: create from first few words of task
        words = task_description.lower().split()[:3]
        fallback_name = "_".join(word.strip(".,!?") for word in words if word.isalnum())
        return format_python_name(fallback_name) or "simple_project"


def get_project_directory(
    base_output_dir: Path, 
    project_name: Optional[str] = None, 
    task_description: Optional[str] = None
) -> Path:
    """Get or create project directory with auto-generated name if needed."""
    
    if not project_name:
        if task_description:
            project_name = generate_project_name(task_description)
        else:
            project_name = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Ensure project name is valid
    project_name = format_python_name(project_name)
    
    # Create project directory
    project_dir = base_output_dir / project_name
    project_dir.mkdir(parents=True, exist_ok=True)
    
    return project_dir


def create_project_subdirectory(project_dir: Path, subdir_name: str) -> Path:
    """Create a subdirectory within a project directory."""
    
    subdir = project_dir / subdir_name
    subdir.mkdir(parents=True, exist_ok=True)
    
    return subdir