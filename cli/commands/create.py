"""
Create command - Generate agents, collaborations, and tools.
"""

from pathlib import Path
from typing import Dict, Any, Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from cli.templates.generators import generate_tool_file as gen_tool
from cli.templates.generators import generate_collaboration_project
from cli.templates.generators import generate_agent_project

from cli.utils import (
    load_yaml_file, format_python_name, prompt_for_tools,
    show_success_message, show_error_message, get_project_directory, create_project_subdirectory
)

console = Console()


@click.group()
def create():
    """
    Create agents, collaborations, and tools.
    
    Generate Python code for AI agents and multi-agent collaborations
    using templates and AI-powered suggestions.
    """
    pass


@create.command()
@click.argument("name", required=False)
@click.option(
    "--from-plan",
    type=click.Path(exists=True),
    help="Create agents from a plan.yaml file",
)
@click.option(
    "--system-prompt",
    "-p",
    help="System prompt for the agent",
)
@click.option(
    "--tools",
    "-t",
    help="Comma-separated list of tools",
)
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Interactive agent creation",
)
@click.option(
    "--memory/--no-memory",
    default=True,
    help="Enable/disable agent memory",
)
@click.option(
    "--memory-size",
    type=int,
    default=20,
    help="Memory size for the agent",
)
@click.pass_context
def agent(
    ctx,
    name: Optional[str],
    from_plan: Optional[str],
    system_prompt: Optional[str],
    tools: Optional[str],
    interactive: bool,
    memory: bool,
    memory_size: int,
):
    """
    Create a single AI agent.
    
    Examples:
      simpleai create agent WeatherBot --system-prompt "You help with weather" --tools "get_weather,get_forecast"
      simpleai create agent --from-plan plan.yaml
      simpleai create agent MyAgent --interactive
    """
    base_output_dir = ctx.obj["output_dir"]
    project_name = ctx.obj.get("project_name")
    
    if from_plan:
        create_agents_from_plan(from_plan, base_output_dir, project_name)
    elif interactive:
        create_agent_interactive(base_output_dir, project_name, name)
    else:
        if not name:
            console.print("[red]Error: Agent name is required when not using --from-plan or --interactive[/red]")
            return
        
        create_single_agent(
            name, system_prompt, tools, memory, memory_size, base_output_dir, project_name
        )


@create.command()
@click.argument("name", required=False)
@click.option(
    "--from-plan",
    type=click.Path(exists=True),
    help="Create collaboration from a plan.yaml file",
)
@click.option(
    "--agents",
    "-a",
    help="Comma-separated list of agent names or files",
)
@click.option(
    "--shared-memory/--no-shared-memory",
    default=True,
    help="Enable/disable shared memory between agents",
)
@click.option(
    "--memory-size",
    type=int,
    default=50,
    help="Shared memory size",
)
@click.pass_context
def collaboration(
    ctx,
    name: Optional[str],
    from_plan: Optional[str],
    agents: Optional[str],
    shared_memory: bool,
    memory_size: int,
):
    """
    Create a multi-agent collaboration.
    
    Examples:
      simpleai create collaboration TeamWork --agents "agent1.py,agent2.py"
      simpleai create collaboration --from-plan plan.yaml
    """
    base_output_dir = ctx.obj["output_dir"]
    project_name = ctx.obj.get("project_name")
    
    if from_plan:
        create_collaboration_from_plan(from_plan, base_output_dir, project_name)
    else:
        if not name or not agents:
            console.print("[red]Error: Both name and agents are required when not using --from-plan[/red]")
            return
        
        create_collaboration_from_agents(
            name, agents, shared_memory, memory_size, base_output_dir, project_name
        )


@create.command()
@click.argument("name")
@click.option(
    "--description",
    "-d",
    help="Tool description",
)
@click.option(
    "--parameters",
    "-p",
    help="JSON string of parameters schema",
)
@click.pass_context
def tool(ctx, name: str, description: Optional[str], parameters: Optional[str]):
    """
    Create a custom tool template.
    
    Example:
      simpleai create tool get_weather --description "Get weather for a city"
    """
    base_output_dir = ctx.obj["output_dir"]
    project_name = ctx.obj.get("project_name")
    create_tool_template(name, description, parameters, base_output_dir, project_name)


def create_single_agent(
    name: str,
    system_prompt: Optional[str],
    tools_str: Optional[str],
    use_memory: bool,
    memory_size: int,
    base_output_dir: Path,
    project_name: Optional[str] = None,
):
    """Create a single agent with the given parameters."""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"🤖 Creating agent {name}...", total=None)
        
        try:
            # Format name
            agent_name = format_python_name(name)
            
            # Parse tools
            tools = []
            if tools_str:
                tool_names = [t.strip() for t in tools_str.split(",")]
                tools = [{"name": tool, "description": f"Tool: {tool}"} for tool in tool_names]
            
            # Use default system prompt if not provided
            if not system_prompt:
                system_prompt = f"You are {agent_name}, a helpful AI assistant."
            
            # Create agent data
            agent_data = {
                "name": agent_name,
                "system_prompt": system_prompt,
                "tools": tools,
                "use_memory": use_memory,
                "memory_size": memory_size,
            }
            
            # Get project directory and create agents subdirectory  
            project_dir = get_project_directory(base_output_dir, project_name, f"Create {agent_name} agent")
            agents_dir = create_project_subdirectory(project_dir, "agents")
            agent_dir = agents_dir / agent_name
            
            # Generate agent files
            generate_agent_files(agent_data, agent_dir)
            
            progress.update(task, description="✅ Agent created successfully")
            
            # Show success message with clear next steps
            show_success_message(
                f"🤖 Agent Created: {agent_name}",
                f"Your agent is ready! Files generated in {agent_dir}",
                [
                    f"cd {agent_dir}  # Navigate to your agent",
                    "python example_usage.py  # Test your agent", 
                    f"simpleai run {agent_name.lower()}_agent.py \"Hello!\"  # Run your agent",
                    f"📁 Project structure: {project_dir.name}/agents/{agent_name}/"
                ]
            )
            
        except Exception as e:
            progress.update(task, description="❌ Agent creation failed")
            show_error_message("Creation Failed", str(e))


def create_agent_interactive(base_output_dir: Path, project_name: Optional[str] = None, agent_name: Optional[str] = None):
    """Create an agent interactively."""
    
    console.print("\n[bold blue]🤖 Interactive Agent Creation[/bold blue]")
    
    # Get agent name
    if not agent_name:
        name = Prompt.ask("Enter agent name")
        agent_name = format_python_name(name)
    else:
        agent_name = format_python_name(agent_name)
    
    # Get system prompt
    system_prompt = Prompt.ask(
        "Enter system prompt",
        default=f"You are {agent_name}, a helpful AI assistant."
    )
    
    # Get tools
    console.print("\n[bold]Tool Configuration:[/bold]")
    if Confirm.ask("Add tools to this agent?", default=True):
        tools = prompt_for_tools()
    else:
        tools = []
    
    # Memory settings
    use_memory = Confirm.ask("Enable memory?", default=True)
    memory_size = 20
    if use_memory:
        memory_size = int(Prompt.ask("Memory size", default="20"))
    
    # Create the agent
    create_single_agent(
        agent_name, system_prompt, None, use_memory, memory_size, base_output_dir, project_name
    )


def create_agents_from_plan(plan_file: str, base_output_dir: Path, project_name: Optional[str] = None):
    """Create agents from a plan file."""
    
    try:
        plan_file_path = Path(plan_file)
        plan_data = load_yaml_file(plan_file_path)
        agents = plan_data.get("agents", [])
        
        if not agents:
            console.print("[red]No agents found in plan file[/red]")
            return
        
        # Detect existing project directory from plan file location
        # Plan file should be at: outputs/project_name/plan/plan.yaml
        # So project directory is: outputs/project_name/
        if plan_file_path.parent.name == "plan":
            existing_project_dir = plan_file_path.parent.parent
            console.print(f"[blue]Using existing project directory: {existing_project_dir}[/blue]")
        else:
            # Fallback to creating new project directory
            meta = plan_data.get("meta", {})
            task_description = meta.get("task_description", "Create agents from plan")
            existing_project_dir = get_project_directory(base_output_dir, project_name, task_description)
        
        console.print(f"[blue]Creating {len(agents)} agents from plan...[/blue]")
        
        for agent_data in agents:
            agent_name = format_python_name(agent_data.get("name", "Agent"))
            
            # Create agent with plan data, using existing project directory
            create_single_agent_in_project(
                agent_name,
                agent_data.get("system_prompt"),
                ",".join(agent_data.get("tools", [])),
                True,  # Use memory by default
                20,    # Default memory size
                existing_project_dir
            )
        
        # Also create collaboration if needed
        collaboration = plan_data.get("collaboration", {})
        if collaboration.get("needed", False):
            create_collaboration_from_plan_data_in_project(plan_data, existing_project_dir)
            
    except Exception as e:
        show_error_message("Plan Processing Failed", str(e))


def create_collaboration_from_plan(plan_file: str, base_output_dir: Path, project_name: Optional[str] = None):
    """Create collaboration from plan file."""
    
    try:
        plan_file_path = Path(plan_file)
        plan_data = load_yaml_file(plan_file_path)
        
        # Detect existing project directory from plan file location
        if plan_file_path.parent.name == "plan":
            existing_project_dir = plan_file_path.parent.parent
            console.print(f"[blue]Using existing project directory: {existing_project_dir}[/blue]")
        else:
            # Fallback to creating new project directory
            meta = plan_data.get("meta", {})
            task_description = meta.get("task_description", "Create collaboration from plan")
            existing_project_dir = get_project_directory(base_output_dir, project_name, task_description)
        
        create_collaboration_from_plan_data_in_project(plan_data, existing_project_dir)
    except Exception as e:
        show_error_message("Collaboration Creation Failed", str(e))


def create_collaboration_from_plan_data(plan_data: Dict[str, Any], base_output_dir: Path, project_name: Optional[str] = None):
    """Create collaboration from plan data."""
    
    agents = plan_data.get("agents", [])
    collaboration = plan_data.get("collaboration", {})
    meta = plan_data.get("meta", {})
    
    if not agents:
        console.print("[red]No agents found in plan[/red]")
        return
    
    # Generate collaboration name from the main agent or task description
    if len(agents) == 1:
        # Single agent - create individual agent, not collaboration
        agent_data = agents[0]
        agent_name = format_python_name(agent_data.get("name", "Agent"))
        
        # Get project directory using task description from meta
        task_description = meta.get("task_description", "Create agent from plan")
        project_dir = get_project_directory(base_output_dir, project_name, task_description)
        agents_dir = create_project_subdirectory(project_dir, "agents")
        agent_dir = agents_dir / agent_name
        
        # Create single agent
        create_single_agent(
            agent_name,
            agent_data.get("system_prompt"),
            ",".join(agent_data.get("tools", [])),
            True,  # Use memory by default
            20,    # Default memory size
            base_output_dir,
            project_name
        )
        return
    
    # Multiple agents - create collaboration with meaningful name
    main_agent_name = format_python_name(agents[0].get("name", "Team"))
    collab_name = f"{main_agent_name}Collaboration"
    
    # Create collaboration data
    collab_data = {
        "name": collab_name,
        "agents": [format_python_name(agent.get("name", f"Agent{i}")) for i, agent in enumerate(agents)],
        "shared_memory": collaboration.get("shared_memory", True),
        "memory_size": 50,
        "execution_type": collaboration.get("type", "sequential"),
    }
    
    # Get project directory using task description from meta
    task_description = meta.get("task_description", "Create collaboration from plan")
    project_dir = get_project_directory(base_output_dir, project_name, task_description)
    agents_dir = create_project_subdirectory(project_dir, "agents")
    collab_dir = agents_dir / collab_data["name"]
    
    generate_collaboration_files(collab_data, collab_dir)
    
    show_success_message(
        "📦 Collaboration Created",
        f"Your multi-agent collaboration is ready! Files generated in {collab_dir}",
        [
            f"cd {collab_dir}  # Navigate to your collaboration",
            "python example_usage.py  # Test your collaboration",
            f"simpleai run {collab_data['name'].lower()}_collaboration.py \"Your task here\"  # Run collaboration",
            f"📁 Project structure: {project_dir.name}/agents/{collab_data['name']}/"
        ]
    )


def create_collaboration_from_agents(
    name: str,
    agents_str: str,
    shared_memory: bool,
    memory_size: int,
    base_output_dir: Path,
    project_name: Optional[str] = None,
):
    """Create collaboration from existing agents."""
    
    agent_files = [a.strip() for a in agents_str.split(",")]
    
    collab_data = {
        "name": format_python_name(name),
        "agent_files": agent_files,
        "shared_memory": shared_memory,
        "memory_size": memory_size,
        "execution_type": "sequential",
    }
    
    # Get project directory and create agents subdirectory  
    project_dir = get_project_directory(base_output_dir, project_name, f"Create {name} collaboration")
    agents_dir = create_project_subdirectory(project_dir, "agents")
    collab_dir = agents_dir / collab_data["name"]
    
    generate_collaboration_files(collab_data, collab_dir)
    
    show_success_message(
        f"📦 Collaboration Created: {name}",
        f"Your multi-agent collaboration is ready! Files generated in {project_dir}",
        [
            f"cd {project_dir}  # Navigate to your collaboration",
            "python example_usage.py  # Test your collaboration",
            f"simpleai run {collab_data['name'].lower()}_collaboration.py \"Your task here\"  # Run collaboration"
        ]
    )


def create_tool_template(
    name: str,
    description: Optional[str],
    parameters: Optional[str],
    base_output_dir: Path,
    project_name: Optional[str] = None,
):
    """Create a tool template."""
    
    tool_name = format_python_name(name)
    
    tool_data = {
        "name": tool_name,
        "description": description or f"Custom tool: {tool_name}",
        "parameters": parameters or "{}",
    }
    
    # Get project directory and create tools subdirectory  
    project_dir = get_project_directory(base_output_dir, project_name, f"Create {tool_name} tool")
    tools_dir = create_project_subdirectory(project_dir, "tools")
    
    tool_file = tools_dir / f"{tool_name}.py"
    generate_tool_file(tool_data, tool_file)
    
    show_success_message(
        f"🔧 Tool Created: {tool_name}",
        f"Your tool template is ready! Saved to {tool_file}",
        [
            f"Edit {tool_file}  # Implement your tool logic",
            "Add it to an agent with --tools option",
            "Test it in your agent projects"
        ]
    )


def generate_agent_files(agent_data: Dict[str, Any], project_dir: Path):
    """Generate agent files from template."""
    generate_agent_project(agent_data, project_dir)


def generate_collaboration_files(collab_data: Dict[str, Any], project_dir: Path):
    """Generate collaboration files from template."""
    generate_collaboration_project(collab_data, project_dir)


def generate_tool_file(tool_data: Dict[str, Any], tool_file: Path):
    """Generate tool file from template."""
    gen_tool(tool_data, tool_file)


def create_single_agent_in_project(
    name: str,
    system_prompt: Optional[str],
    tools_str: Optional[str],
    use_memory: bool,
    memory_size: int,
    project_dir: Path,
):
    """Create a single agent within an existing project directory."""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"🤖 Creating agent {name}...", total=None)
        
        try:
            # Format name
            agent_name = format_python_name(name)
            
            # Parse tools
            tools = []
            if tools_str:
                tool_names = [t.strip() for t in tools_str.split(",")]
                tools = [{"name": tool, "description": f"Tool: {tool}"} for tool in tool_names]
            
            # Use default system prompt if not provided
            if not system_prompt:
                system_prompt = f"You are {agent_name}, a helpful AI assistant."
            
            # Create agent data
            agent_data = {
                "name": agent_name,
                "system_prompt": system_prompt,
                "tools": tools,
                "use_memory": use_memory,
                "memory_size": memory_size,
            }
            
            # Create project subdirectory for this agent
            project_subdir = create_project_subdirectory(project_dir, "project")
            agents_dir = create_project_subdirectory(project_subdir, "agents")
            agent_dir = agents_dir / agent_name
            
            # Generate agent files
            generate_agent_files(agent_data, agent_dir)
            
            progress.update(task, description="✅ Agent created successfully")
            
            # Show success message with clear next steps
            show_success_message(
                f"🤖 Agent Created: {agent_name}",
                f"Your agent is ready! Files generated in {agent_dir}",
                [
                    f"cd {agent_dir}  # Navigate to your agent",
                    "python example_usage.py  # Test your agent", 
                    f"simpleai run {agent_name.lower()}_agent.py \"Hello!\"  # Run your agent",
                    f"📁 Project structure: {project_dir.name}/project/agents/{agent_name}/"
                ]
            )
            
        except Exception as e:
            progress.update(task, description="❌ Agent creation failed")
            show_error_message("Creation Failed", str(e))


def create_collaboration_from_plan_data_in_project(plan_data: Dict[str, Any], project_dir: Path):
    """Create collaboration from plan data within an existing project directory."""
    
    agents = plan_data.get("agents", [])
    collaboration = plan_data.get("collaboration", {})
    meta = plan_data.get("meta", {})
    
    if not agents:
        console.print("[red]No agents found in plan[/red]")
        return
    
    # Generate collaboration name from the main agent or task description
    if len(agents) == 1:
        # Single agent - create individual agent, not collaboration
        agent_data = agents[0]
        agent_name = format_python_name(agent_data.get("name", "Agent"))
        
        # Create single agent in project
        create_single_agent_in_project(
            agent_name,
            agent_data.get("system_prompt"),
            ",".join(agent_data.get("tools", [])),
            True,  # Use memory by default
            20,    # Default memory size
            project_dir
        )
        return
    
    # Multiple agents - create collaboration with meaningful name
    main_agent_name = format_python_name(agents[0].get("name", "Team"))
    collab_name = f"{main_agent_name}Collaboration"
    
    # Create enhanced collaboration data with agent details from plan
    collab_data = {
        "name": collab_name,
        "agents": [format_python_name(agent.get("name", f"Agent{i}")) for i, agent in enumerate(agents)],
        "agent_details": agents,  # Pass full agent details for smart generation
        "shared_memory": collaboration.get("shared_memory", True),
        "memory_size": 50,
        "execution_type": collaboration.get("type", "sequential"),
        "task_description": meta.get("task_description", "Multi-agent collaboration")
    }
    
    # Create project subdirectory and agents directory
    project_subdir = create_project_subdirectory(project_dir, "project")
    agents_dir = create_project_subdirectory(project_subdir, "agents")
    collab_dir = agents_dir / collab_data["name"]
    
    generate_collaboration_files(collab_data, collab_dir)
    
    show_success_message(
        "📦 Collaboration Created",
        f"Your multi-agent collaboration is ready! Files generated in {collab_dir}",
        [
            f"cd {collab_dir}  # Navigate to your collaboration",
            "python example_usage.py  # Test your collaboration",
            f"simpleai run {collab_data['name'].lower()}_collaboration.py \"Your task here\"  # Run collaboration",
            f"📁 Project structure: {project_dir.name}/project/agents/{collab_data['name']}/"
        ]
    )