"""
Main CLI entry point for SimpleAI.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from dotenv import load_dotenv

# Add simpleai to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.commands.plan import plan
from cli.commands.create import create
from cli.commands.run import run
from cli.commands.generate import generate


console = Console()


@click.group()
@click.option(
    "--output-dir",
    "-o",
    default="outputs",
    help="Base directory for output files",
    type=click.Path(),
)
@click.option(
    "--project-name",
    "-p",
    help="Project name for organizing outputs (auto-generated if not provided)",
)
@click.option(
    "--config-file",
    "-c",
    help="Configuration file path",
    type=click.Path(exists=True),
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.pass_context
def cli(ctx, output_dir: str, project_name: Optional[str], config_file: Optional[str], verbose: bool):
    """
    SimpleAI CLI - Create and manage AI agents and collaborations.
    
    A powerful command-line interface for the SimpleAI framework that helps you
    plan, create, run, and generate AI agents and multi-agent collaborations.
    """
    # Load environment variables from .env file if it exists
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv(env_file)
        if verbose:
            console.print(f"✓ Loaded configuration from {env_file}", style="dim green")
    
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Store global configuration
    ctx.obj["output_dir"] = Path(output_dir)
    ctx.obj["project_name"] = project_name
    ctx.obj["config_file"] = config_file
    ctx.obj["verbose"] = verbose
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Set logging level based on verbose flag
    if verbose:
        os.environ["LOG_LEVEL"] = "DEBUG"
    elif "LOG_LEVEL" not in os.environ:
        os.environ["LOG_LEVEL"] = "INFO"
    
    # Check for API keys and auto-configure SimpleAI if available
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    if verbose and os.getenv("LOG_LEVEL") == "DEBUG":
        console.print(f"🔍 DEBUG: OpenAI key present: {has_openai}", style="dim")
        console.print(f"🔍 DEBUG: Anthropic key present: {has_anthropic}", style="dim")
    
    # Auto-configure SimpleAI if API keys are available
    if has_openai or has_anthropic:
        try:
            from core import SimpleAI
            
            # Check if already configured
            try:
                config = SimpleAI.get_config()
                if config:
                    if verbose:
                        console.print("✓ SimpleAI already configured", style="dim green")
                else:
                    raise Exception("Not configured")
            except:
                # Not configured, so configure it
                provider = os.getenv("SIMPLEAI_PROVIDER")
                model = os.getenv("SIMPLEAI_MODEL")
                
                # Auto-detect provider if not specified
                if not provider:
                    provider = "openai" if has_openai else "claude"
                
                # Set default model if not specified
                if not model:
                    if provider == "openai":
                        model = "gpt-4o-mini"
                    else:
                        model = "claude-3-5-sonnet-20241022"
                
                SimpleAI.configure(provider=provider, model=model)
                
                if verbose:
                    console.print(f"✓ Auto-configured SimpleAI: {provider} ({model})", style="dim green")
                
        except Exception as e:
            if verbose and os.getenv("LOG_LEVEL") == "DEBUG":
                console.print(f"🔍 DEBUG: Failed to auto-configure SimpleAI: {e}", style="dim red")
    
    elif ctx.invoked_subcommand not in [None, "configure"]:
        console.print("⚠️  No API keys found. Use 'simpleai configure' to set up your API keys.", style="yellow")
    
    # Display welcome message
    if ctx.invoked_subcommand is None:
        show_welcome()


def show_welcome():
    """Display welcome message and usage information."""
    welcome_text = Text()
    welcome_text.append("SimpleAI CLI", style="bold blue")
    welcome_text.append(" - AI Agent Framework\n\n", style="blue")
    welcome_text.append("Available Commands:\n", style="bold")
    welcome_text.append("  configure", style="green")
    welcome_text.append("- Set up API keys and configuration\n")
    welcome_text.append("  plan     ", style="green")
    welcome_text.append("- Analyze tasks and suggest AI agent architectures\n")
    welcome_text.append("  create   ", style="green")
    welcome_text.append("- Generate agents, collaborations, and tools\n")
    welcome_text.append("  generate ", style="green")
    welcome_text.append("- Create examples and project templates\n")
    welcome_text.append("  run      ", style="green")
    welcome_text.append("- Execute agents and collaborations\n\n")
    welcome_text.append("Use --help with any command for detailed information.", style="dim")
    
    panel = Panel(
        welcome_text,
        title="🤖 Welcome to SimpleAI",
        border_style="blue",
        padding=(1, 2),
    )
    console.print(panel)


# Configure command
@cli.command()
@click.option("--provider", type=click.Choice(["openai", "anthropic"]), help="AI provider to configure")
@click.option("--api-key", help="API key for the selected provider")
@click.option("--model", help="Default model to use")
def configure(provider: Optional[str], api_key: Optional[str], model: Optional[str]):
    """Set up API keys and configuration for SimpleAI."""
    env_file = Path(".env")
    
    # Interactive configuration if no options provided
    if not provider:
        console.print("🔧 SimpleAI Configuration Setup", style="bold blue")
        console.print("\nChoose your AI provider:")
        console.print("1. OpenAI (GPT models)")
        console.print("2. Anthropic (Claude models)")
        
        choice = click.prompt("Enter choice (1 or 2)", type=int)
        provider = "openai" if choice == 1 else "anthropic"
    
    if not api_key:
        key_name = "OPENAI_API_KEY" if provider == "openai" else "ANTHROPIC_API_KEY"
        api_key = click.prompt(f"Enter your {provider.upper()} API key", hide_input=True)
    
    if not model:
        default_models = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-5-sonnet-20241022"
        }
        model = click.prompt(f"Enter default model", default=default_models[provider])
    
    # Update or create .env file
    env_content = []
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_content = f.readlines()
    
    # Remove existing entries for this provider
    key_name = "OPENAI_API_KEY" if provider == "openai" else "ANTHROPIC_API_KEY"
    env_content = [line for line in env_content if not line.startswith(f"{key_name}=")]
    env_content = [line for line in env_content if not line.startswith("SIMPLEAI_PROVIDER=")]
    env_content = [line for line in env_content if not line.startswith("SIMPLEAI_MODEL=")]
    
    # Add new configuration entries
    env_content.append(f"{key_name}={api_key}\n")
    env_content.append(f"SIMPLEAI_PROVIDER={provider}\n")
    env_content.append(f"SIMPLEAI_MODEL={model}\n")
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.writelines(env_content)
    
    console.print(f"✅ Configuration saved to {env_file}", style="green")
    console.print(f"   Provider: {provider}")
    console.print(f"   Model: {model}")
    console.print(f"   API Key: {'*' * (len(api_key) - 4) + api_key[-4:]}")


# Add commands to the main CLI group in the desired order
cli.add_command(plan)
cli.add_command(create)
cli.add_command(generate)
cli.add_command(run)


if __name__ == "__main__":
    cli()