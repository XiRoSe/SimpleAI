"""
Run command - Execute agents and collaborations.
"""

import sys
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from cli.utils import (
    ensure_simpleai_configured, create_timestamped_dir, save_json_file,
    show_success_message, show_error_message
)

console = Console()


@click.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.argument("input_message")
@click.option(
    "--save-results/--no-save-results",
    default=True,
    help="Save execution results to output directory",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "text", "both"]),
    default="both",
    help="Output format for results",
)
@click.option(
    "--stream/--no-stream",
    default=False,
    help="Enable streaming output (if supported)",
)
@click.option(
    "--verbose/--quiet",
    default=False,
    help="Verbose output with execution details",
)
@click.pass_context
def run(
    ctx,
    file_path: str,
    input_message: str,
    save_results: bool,
    output_format: str,
    stream: bool,
    verbose: bool,
):
    """
    Execute an AI agent or collaboration.
    
    Runs the specified Python file containing an agent or collaboration
    and executes it with the provided input message.
    
    Examples:
      simpleai run my_agent.py "Hello, how are you?"
      simpleai run collaboration.py "Analyze this data and create a report"
      simpleai run agent.py "Your message" --format json --no-save-results
    """
    output_dir = ctx.obj["output_dir"]
    
    # Ensure SimpleAI is configured
    ensure_simpleai_configured()
    
    # Create execution session
    session_dir = None
    if save_results:
        session_dir = create_timestamped_dir(output_dir / "runs", "run_")
    
    # Execute the file
    try:
        result = execute_file(
            Path(file_path),
            input_message,
            stream=stream,
            verbose=verbose,
            session_dir=session_dir
        )
        
        # Display results
        display_results(result, output_format, verbose)
        
        # Save results if requested
        if save_results and session_dir:
            save_execution_results(result, session_dir, output_format)
            console.print(f"\n📁 Results saved to: [green]{session_dir}[/green]")
        
        # Show success message with next steps
        show_execution_success(result, Path(file_path), save_results, session_dir)
        
    except Exception as e:
        show_error_message(
            "Execution Failed",
            f"Failed to execute {file_path}: {str(e)}",
            [
                "Check that the file contains a valid agent or collaboration",
                "Ensure all dependencies are installed",
                "Verify the file has the required functions or classes"
            ]
        )
        sys.exit(1)


def execute_file(
    file_path: Path,
    input_message: str,
    stream: bool = False,
    verbose: bool = False,
    session_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """Execute a Python file containing an agent or collaboration."""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        disable=not verbose,
    ) as progress:
        
        if verbose:
            task = progress.add_task("🚀 Loading module...", total=None)
        
        # Load the Python module
        try:
            spec = importlib.util.spec_from_file_location("agent_module", file_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load module from {file_path}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules["agent_module"] = module
            spec.loader.exec_module(module)
            
        except Exception as e:
            raise RuntimeError(f"Failed to load module: {e}")
        
        if verbose:
            progress.update(task, description="🔍 Detecting execution type...")
        
        # Detect what type of execution this is
        execution_type, executor = detect_execution_type(module)
        
        if verbose:
            progress.update(task, description=f"⚡ Executing {execution_type}...")
        
        # Record execution metadata
        start_time = datetime.now()
        
        try:
            # Execute based on type
            if execution_type == "agent":
                result = execute_agent(executor, input_message, stream)
            elif execution_type == "collaboration":
                result = execute_collaboration(executor, input_message, stream)
            else:
                raise ValueError(f"Unknown execution type: {execution_type}")
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            if verbose:
                progress.update(task, description="✅ Execution completed")
            
            # Build result metadata
            execution_result = {
                "file_path": str(file_path),
                "input_message": input_message,
                "execution_type": execution_type,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "execution_time_seconds": execution_time,
                "success": True,
                "result": result,
                "metadata": {
                    "stream_enabled": stream,
                    "session_dir": str(session_dir) if session_dir else None,
                }
            }
            
            return execution_result
            
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            if verbose:
                progress.update(task, description="❌ Execution failed")
            
            # Build error result
            execution_result = {
                "file_path": str(file_path),
                "input_message": input_message,
                "execution_type": execution_type,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "execution_time_seconds": execution_time,
                "success": False,
                "error": str(e),
                "metadata": {
                    "stream_enabled": stream,
                    "session_dir": str(session_dir) if session_dir else None,
                }
            }
            
            raise RuntimeError(f"Execution failed: {e}")


def detect_execution_type(module):
    """Detect whether this is an agent or collaboration module."""
    
    # Look for common patterns
    
    # Check for create_agent function (single agent)
    if hasattr(module, 'create_agent'):
        return "agent", module.create_agent
    
    # Check for create_collaboration function (collaboration)
    if hasattr(module, 'create_collaboration'):
        return "collaboration", module.create_collaboration
    
    # Check for agent class pattern
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if hasattr(attr, '__call__') and not attr_name.startswith('_'):
            # Check if it looks like an agent class
            try:
                instance = attr()
                if hasattr(instance, 'chat') or hasattr(instance, 'execute'):
                    if hasattr(instance, 'execute'):
                        return "collaboration", attr
                    else:
                        return "agent", attr
            except:
                continue
    
    raise ValueError(
        "Cannot detect execution type. File should contain:\n"
        "- create_agent() function for single agents\n"
        "- create_collaboration() function for collaborations\n"
        "- Or a class with chat() or execute() methods"
    )


def execute_agent(agent_creator, input_message: str, stream: bool = False) -> Dict[str, Any]:
    """Execute a single agent."""
    
    # Create agent instance
    if callable(agent_creator):
        agent = agent_creator()
    else:
        agent = agent_creator
    
    # Execute the chat
    if stream and hasattr(agent, 'chat'):
        # For streaming, we'll collect the stream (simplified for now)
        response = agent.chat(input_message, stream=False)  # TODO: Implement streaming
    else:
        if hasattr(agent, 'chat'):
            response = agent.chat(input_message)
        else:
            raise ValueError("Agent does not have a chat() method")
    
    # Get memory stats if available
    memory_stats = {}
    if hasattr(agent, 'get_memory_stats'):
        try:
            memory_stats = agent.get_memory_stats()
        except:
            pass
    
    return {
        "type": "agent_response",
        "response": response,
        "memory_stats": memory_stats,
    }


def execute_collaboration(collab_creator, input_message: str, stream: bool = False) -> Dict[str, Any]:
    """Execute a collaboration."""
    
    # Create collaboration instance
    if callable(collab_creator):
        collaboration = collab_creator()
    else:
        collaboration = collab_creator
    
    # Execute the task
    if hasattr(collaboration, 'execute'):
        result = collaboration.execute(input_message)
    else:
        raise ValueError("Collaboration does not have an execute() method")
    
    # Get memory stats if available
    memory_stats = {}
    if hasattr(collaboration, 'get_memory_stats'):
        try:
            memory_stats = collaboration.get_memory_stats()
        except:
            pass
    
    return {
        "type": "collaboration_result",
        "task": input_message,
        "plan": result.get("plan", []),
        "results": result.get("results", []),
        "memory": result.get("memory", []),
        "memory_stats": memory_stats,
    }


def display_results(execution_result: Dict[str, Any], output_format: str, verbose: bool):
    """Display execution results in the specified format."""
    
    if not execution_result["success"]:
        console.print(f"[red]❌ Execution failed: {execution_result.get('error', 'Unknown error')}[/red]")
        return
    
    result = execution_result["result"]
    execution_time = execution_result["execution_time_seconds"]
    
    # Show execution summary
    if verbose:
        console.print(f"\n[green]✅ Execution completed in {execution_time:.2f}s[/green]")
        console.print(f"[dim]File: {execution_result['file_path']}[/dim]")
        console.print(f"[dim]Input: {execution_result['input_message'][:100]}{'...' if len(execution_result['input_message']) > 100 else ''}[/dim]")
    
    # Display results based on type
    if result["type"] == "agent_response":
        display_agent_results(result, output_format, verbose)
    elif result["type"] == "collaboration_result":
        display_collaboration_results(result, output_format, verbose)


def display_agent_results(result: Dict[str, Any], output_format: str, verbose: bool):
    """Display single agent results."""
    
    response = result["response"]
    memory_stats = result.get("memory_stats", {})
    
    if output_format in ["text", "both"]:
        # Text output
        console.print("\n[bold blue]🤖 Agent Response:[/bold blue]")
        
        # Create a panel for the response
        response_text = Text(str(response))
        panel = Panel(response_text, title="Response", border_style="blue", padding=(1, 2))
        console.print(panel)
        
        # Show memory stats if verbose
        if verbose and memory_stats:
            console.print(f"\n[bold blue]📊 Memory Stats:[/bold blue]")
            console.print(f"  Entries: {memory_stats.get('entries', 0)}")
            console.print(f"  Max Entries: {memory_stats.get('max_entries', 0)}")
            tools_used = memory_stats.get('tools_used', [])
            if tools_used:
                console.print(f"  Tools Used: {', '.join(tools_used)}")
    
    if output_format in ["json", "both"]:
        # JSON output
        if output_format == "both":
            console.print("\n[bold blue]📄 JSON Output:[/bold blue]")
        
        json_data = {
            "response": response,
            "memory_stats": memory_stats,
        }
        
        console.print_json(data=json_data)


def display_collaboration_results(result: Dict[str, Any], output_format: str, verbose: bool):
    """Display collaboration results."""
    
    task = result["task"]
    plan = result.get("plan", [])
    results = result.get("results", [])
    memory_stats = result.get("memory_stats", {})
    
    if output_format in ["text", "both"]:
        # Text output
        console.print(f"\n[bold blue]🤝 Collaboration Results:[/bold blue]")
        console.print(f"[bold]Task:[/bold] {task}")
        
        # Show execution plan if verbose
        if verbose and plan:
            console.print(f"\n[bold blue]📋 Execution Plan:[/bold blue]")
            plan_table = Table(show_header=True, header_style="bold magenta")
            plan_table.add_column("Step", style="cyan", width=6)
            plan_table.add_column("Agent", style="green")
            plan_table.add_column("Action", style="white")
            
            for step in plan:
                plan_table.add_row(
                    str(step.get("step", "?")),
                    step.get("agent", "Unknown"),
                    step.get("action", "No action")[:50] + ("..." if len(step.get("action", "")) > 50 else "")
                )
            console.print(plan_table)
        
        # Show results
        console.print(f"\n[bold blue]📊 Agent Results:[/bold blue]")
        
        for i, step_result in enumerate(results):
            agent_name = step_result.get("agent", "Unknown")
            status = step_result.get("status", "unknown")
            output = step_result.get("output", "No output")
            
            status_style = "green" if status == "success" else "red"
            status_emoji = "✅" if status == "success" else "❌"
            
            console.print(f"\n[bold]{status_emoji} {agent_name}[/bold] [{status_style}]({status})[/{status_style}]:")
            
            # Create panel for agent output
            output_text = Text(str(output))
            panel = Panel(
                output_text,
                title=f"{agent_name} Output",
                border_style=status_style,
                padding=(1, 2)
            )
            console.print(panel)
        
        # Show memory stats if verbose
        if verbose and memory_stats:
            console.print(f"\n[bold blue]📊 Memory Stats:[/bold blue]")
            console.print(f"  Entries: {memory_stats.get('entries', 0)}")
            agent_contributions = memory_stats.get('agent_contributions', {})
            if agent_contributions:
                console.print("  Agent Contributions:")
                for agent, count in agent_contributions.items():
                    console.print(f"    {agent}: {count}")
    
    if output_format in ["json", "both"]:
        # JSON output
        if output_format == "both":
            console.print("\n[bold blue]📄 JSON Output:[/bold blue]")
        
        json_data = {
            "task": task,
            "plan": plan,
            "results": results,
            "memory_stats": memory_stats,
        }
        
        console.print_json(data=json_data)


def show_execution_success(
    execution_result: Dict[str, Any], 
    file_path: Path, 
    save_results: bool, 
    session_dir: Optional[Path]
):
    """Show success message with next-step instructions after execution."""
    
    result = execution_result["result"]
    execution_time = execution_result["execution_time_seconds"]
    
    # Determine title based on execution type
    if result["type"] == "agent_response":
        title = "🤖 Agent Execution Complete"
        message = f"Your agent '{file_path.name}' executed successfully in {execution_time:.2f}s"
    else:
        title = "🤝 Collaboration Execution Complete"  
        message = f"Your collaboration '{file_path.name}' executed successfully in {execution_time:.2f}s"
    
    # Build next steps
    next_steps = []
    
    if save_results and session_dir:
        next_steps.append(f"cd {session_dir}  # View saved results")
        next_steps.append("cat result.txt  # View text output")
        next_steps.append("cat result.json  # View JSON output")
    
    # Add common next steps
    next_steps.extend([
        f"simpleai run {file_path} \"Different message\"  # Try another message",
        "Edit the agent file to modify behavior",
        "simpleai generate examples  # Create more examples"
    ])
    
    show_success_message(title, message, next_steps)


def save_execution_results(
    execution_result: Dict[str, Any],
    session_dir: Path,
    output_format: str
):
    """Save execution results to files."""
    
    # Save full execution result as JSON
    results_file = session_dir / "execution_result.json"
    save_json_file(execution_result, results_file)
    
    # Save just the result data in requested format
    result_data = execution_result["result"]
    
    if output_format in ["json", "both"]:
        result_json_file = session_dir / "result.json"
        save_json_file(result_data, result_json_file)
    
    if output_format in ["text", "both"]:
        result_text_file = session_dir / "result.txt"
        with open(result_text_file, 'w', encoding='utf-8') as f:
            if result_data["type"] == "agent_response":
                f.write(f"Agent Response:\n{result_data['response']}\n")
            elif result_data["type"] == "collaboration_result":
                f.write(f"Task: {result_data['task']}\n\n")
                f.write("Results:\n")
                for step_result in result_data.get("results", []):
                    agent = step_result.get("agent", "Unknown")
                    status = step_result.get("status", "unknown")
                    output = step_result.get("output", "No output")
                    f.write(f"\n{agent} ({status}):\n{output}\n")
    
    # Save metadata
    metadata_file = session_dir / "metadata.json"
    metadata = {
        "file_path": execution_result["file_path"],
        "input_message": execution_result["input_message"],
        "execution_type": execution_result["execution_type"],
        "start_time": execution_result["start_time"],
        "end_time": execution_result["end_time"],
        "execution_time_seconds": execution_result["execution_time_seconds"],
        "success": execution_result["success"],
        "cli_version": "1.0.0",
    }
    save_json_file(metadata, metadata_file)