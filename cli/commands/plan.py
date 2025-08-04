"""
Plan command - AI-powered task analysis and agent architecture suggestions.
"""

import json
from pathlib import Path
from typing import Dict, Any

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich.prompt import Prompt

from core import SimpleAI
from cli.utils import (
    ensure_simpleai_configured, save_yaml_file, get_project_directory, 
    create_project_subdirectory
)

console = Console()


@click.command()
@click.argument("task_description")
@click.option(
    "--complexity",
    type=click.Choice(["simple", "medium", "complex"]),
    default="medium",
    help="Expected task complexity level",
)
@click.option(
    "--agents",
    "-a",
    type=int,
    help="Preferred number of agents (overrides AI suggestion)",
)
@click.option(
    "--collaboration/--no-collaboration",
    default=None,
    help="Force collaboration on/off (overrides AI suggestion)",
)
@click.option(
    "--save-plan",
    "-s",
    is_flag=True,
    help="Legacy option (plans are now auto-saved when approved)",
)
@click.pass_context
def plan(
    ctx,
    task_description: str,
    complexity: str,
    agents: int,
    collaboration: bool,
    save_plan: bool,
):
    """
    Analyze a task and suggest AI agent architecture.
    
    Uses AI to analyze your task description and recommend:
    - Required agents and their roles
    - Necessary tools for each agent  
    - Whether collaboration is needed
    - Estimated costs and execution time
    
    Example: simpleai plan "Create a marketing strategy for a tech startup"
    """
    base_output_dir = ctx.obj["output_dir"]
    project_name = ctx.obj.get("project_name")
    
    # Get or create project directory
    project_dir = get_project_directory(base_output_dir, project_name, task_description)
    
    if ctx.obj["verbose"]:
        console.print(f"📁 Using project directory: [green]{project_dir}[/green]", style="dim")
    
    # Ensure SimpleAI is configured
    ensure_simpleai_configured()
    
    # Interactive planning loop
    current_plan = None
    iteration = 1
    
    while True:
        console.print(f"\n[bold blue]📋 Planning Iteration {iteration}[/bold blue]")
        
        # Handle user input BEFORE starting progress spinner
        modification_request = None
        if current_plan is not None:
            # Subsequent iterations - get modification request first
            modification_request = get_user_modification_request()
            if not modification_request:
                console.print("[yellow]No modification requested, keeping current plan[/yellow]")
                break
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("🧠 Analyzing task...", total=None)
            
            try:
                # Generate plan using AI
                if current_plan is None:
                    # First iteration - generate initial plan
                    current_plan = generate_ai_plan(
                        task_description, complexity, agents, collaboration
                    )
                else:
                    # Subsequent iterations - modify existing plan
                    if modification_request:
                        current_plan = modify_plan(
                            current_plan, task_description, modification_request
                        )
                
                progress.update(task, description="✅ Analysis complete")
                
            except Exception as e:
                progress.update(task, description="❌ Analysis failed")
                console.print(f"[red]Error: {e}[/red]")
                return
        
        # Display the plan
        display_plan(current_plan, task_description)
        
        # Get user approval
        approval_result = get_user_approval()
        
        if approval_result == "approve":
            console.print("[green]✅ Plan approved![/green]")
            break
        elif approval_result == "modify":
            iteration += 1
            continue
        else:  # cancel
            console.print("[yellow]❌ Planning cancelled[/yellow]")
            return
    
    # Always save approved plans
    plan_subdir = create_project_subdirectory(project_dir, "plan")
    plan_file = plan_subdir / "plan.yaml"
    save_yaml_file(current_plan, plan_file)
    console.print(f"\n📄 Plan saved to: [green]{plan_file}[/green]")
    
    # Show next steps
    show_next_steps(plan_file, project_dir)


def generate_ai_plan(
    task_description: str,
    complexity: str,
    preferred_agents: int,
    force_collaboration: bool,
) -> Dict[str, Any]:
    """Generate an AI-powered plan for the given task."""
    
    # Create planning prompt
    planning_prompt = create_planning_prompt(
        task_description, complexity, preferred_agents, force_collaboration
    )
    
    # Get AI response
    response = SimpleAI.chat(planning_prompt, temperature=0.3)
    
    # Parse the response
    plan_data = parse_ai_response(response, task_description)
    
    return plan_data


def create_planning_prompt(
    task_description: str,
    complexity: str,
    preferred_agents: int,
    force_collaboration: bool,
) -> str:
    """Create the prompt for AI planning."""
    
    prompt = f"""You are an expert AI architecture planner specializing in creating innovative, domain-specific solutions.

Task: {task_description}
Complexity Level: {complexity}

APPROACH: Think creatively and practically about this specific domain. Consider:
- What are the unique challenges and opportunities in this field?
- What specific tools would be most valuable for this exact use case?
- What creative approaches could make this solution stand out?
- How can the agents be specialized for maximum effectiveness?

CREATIVITY GUIDELINES:
- Design agents with specific, meaningful roles (not generic "TaskAgent")
- Create tools that solve real problems in this domain
- Think about realistic workflows and user needs
- Consider edge cases and practical constraints
- Make the solution genuinely useful, not just functional

KEEP IT PRACTICAL: While being creative, ensure the plan is implementable and focused.

Please provide a JSON response with this exact structure:
{{
    "task_analysis": {{
        "description": "Brief analysis of the task",
        "complexity": "simple|medium|complex"
    }},
    "agents": [
        {{
            "name": "AgentName",
            "role": "Brief role description",
            "system_prompt": "Detailed system prompt for the agent",
            "tools": ["tool1", "tool2"],
            "tool_descriptions": {{
                "tool1": "What this tool does",
                "tool2": "What this tool does"
            }}
        }}
    ],
    "collaboration": {{
        "needed": true/false,
        "type": "sequential|parallel|hierarchical",
        "shared_memory": true/false,
        "reasoning": "Why collaboration is/isn't needed"
    }},
    "execution_flow": [
        "Step 1: Agent does X",
        "Step 2: Agent does Y"
    ]
}}

Guidelines:
- Keep it SIMPLE: prefer 1 agent unless truly necessary
- For simple tasks: 1 agent
- For medium tasks: 1-2 agents  
- For complex tasks: 2-3 agents (maximum)
- Always suggest realistic, implementable tools
- Consider if agents need to share information
- Focus on practical, achievable solutions
"""

    if preferred_agents:
        prompt += f"\n- User prefers {preferred_agents} agents"
    
    if force_collaboration is not None:
        collab_pref = "required" if force_collaboration else "not wanted"
        prompt += f"\n- User has {collab_pref} collaboration"
    
    return prompt


def parse_ai_response(response: str, task_description: str) -> Dict[str, Any]:
    """Parse the AI response and extract the plan."""
    
    try:
        # Try to extract JSON from the response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            plan_data = json.loads(json_str)
        else:
            raise ValueError("No JSON found in response")
            
    except (json.JSONDecodeError, ValueError):
        # Fallback: create a basic plan
        plan_data = create_fallback_plan(task_description)
    
    # Add metadata
    plan_data["meta"] = {
        "created_by": "SimpleAI CLI",
        "task_description": task_description,
        "version": "1.0"
    }
    
    return plan_data


def create_fallback_plan(task_description: str) -> Dict[str, Any]:
    """Create a basic fallback plan if AI parsing fails."""
    
    return {
        "task_analysis": {
            "description": f"Analysis of: {task_description}",
            "complexity": "medium"
        },
        "agents": [
            {
                "name": "TaskAgent",
                "role": "Handle the main task",
                "system_prompt": f"You are an AI assistant that helps with: {task_description}",
                "tools": ["general_search", "text_processing"],
                "tool_descriptions": {
                    "general_search": "Search for information",
                    "text_processing": "Process and analyze text"
                }
            }
        ],
        "collaboration": {
            "needed": False,
            "type": "sequential",
            "shared_memory": False,
            "reasoning": "Single agent sufficient for this task"
        },
        "execution_flow": [
            "Step 1: Agent analyzes the input",
            "Step 2: Agent processes the request",
            "Step 3: Agent provides the result"
        ]
    }


def display_plan(plan_data: Dict[str, Any], task_description: str):
    """Display the generated plan in a nice format."""
    
    # Title
    title_text = Text()
    title_text.append("📋 AI-Generated Plan", style="bold blue")
    console.print(Panel(title_text, border_style="blue"))
    
    # Task Analysis
    analysis = plan_data.get("task_analysis", {})
    console.print(f"\n[bold]Task:[/bold] {task_description}")
    console.print(f"[bold]Complexity:[/bold] {analysis.get('complexity', 'medium')}")
    console.print(f"[bold]Description:[/bold] {analysis.get('description', 'No analysis provided')}")
    
    # Agents Table
    agents = plan_data.get("agents", [])
    if agents:
        console.print("\n[bold blue]🤖 Recommended Agents:[/bold blue]")
        
        agents_table = Table(show_header=True, header_style="bold magenta")
        agents_table.add_column("Agent Name", style="cyan")
        agents_table.add_column("Role", style="white")
        agents_table.add_column("Tools", style="green")
        
        for agent in agents:
            tools_str = ", ".join(agent.get("tools", []))
            agents_table.add_row(
                agent.get("name", "Unknown"),
                agent.get("role", "No role specified"),
                tools_str or "No tools"
            )
        
        console.print(agents_table)
    
    # Collaboration Info
    collaboration = plan_data.get("collaboration", {})
    if collaboration:
        console.print(f"\n[bold blue]🤝 Collaboration:[/bold blue]")
        console.print(f"  Needed: {'Yes' if collaboration.get('needed') else 'No'}")
        if collaboration.get("needed"):
            console.print(f"  Type: {collaboration.get('type', 'sequential')}")
            console.print(f"  Shared Memory: {'Yes' if collaboration.get('shared_memory') else 'No'}")
        console.print(f"  Reasoning: {collaboration.get('reasoning', 'Not specified')}")
    
    # Execution Flow
    execution_flow = plan_data.get("execution_flow", [])
    if execution_flow:
        console.print(f"\n[bold blue]⚡ Execution Flow:[/bold blue]")
        for i, step in enumerate(execution_flow, 1):
            console.print(f"  {i}. {step}")


def get_user_approval() -> str:
    """Get user approval for the plan."""
    
    console.print("\n[bold yellow]📋 Plan Review[/bold yellow]")
    
    choice = Prompt.ask(
        "What would you like to do with this plan?",
        choices=["approve", "modify", "cancel"],
        default="approve"
    )
    
    return choice


def get_user_modification_request() -> str:
    """Get user's modification request with helpful guidance."""
    
    console.print("\n[bold blue]✏️  Plan Modification[/bold blue]")
    console.print("Please describe what you'd like to change about the current plan.")
    console.print("\n[bold]What can you modify?[/bold]")
    console.print("🤖 [cyan]Agents:[/cyan] Change number, roles, or specializations")
    console.print("🔧 [cyan]Tools:[/cyan] Add, remove, or modify agent tools")
    console.print("🔄 [cyan]Workflow:[/cyan] Change execution flow or collaboration style")
    console.print("📋 [cyan]Focus:[/cyan] Adjust task scope or emphasis")
    console.print("⚡ [cyan]Complexity:[/cyan] Simplify or add more sophistication")
    
    console.print("\n[bold]Examples:[/bold]")
    console.print("  • 'Add a research agent to gather data before writing'")
    console.print("  • 'Include email marketing tools and social media tools'")
    console.print("  • 'Make it simpler with just one agent'")
    console.print("  • 'Focus more on SEO optimization'")
    console.print("  • 'Add collaboration between agents for review'")
    
    console.print("\n[yellow]💡 Tip: Be specific about what you want to change and why[/yellow]")
    
    modification = Prompt.ask("\n[bold]What changes would you like to make?[/bold]")
    
    # Ask for additional context if the modification seems brief
    if len(modification.split()) < 5:
        additional_context = Prompt.ask(
            "[dim]Any additional details or context? (Press Enter to skip)[/dim]",
            default=""
        )
        if additional_context:
            modification = f"{modification}. {additional_context}"
    
    return modification


def modify_plan(
    current_plan: Dict[str, Any],
    original_task: str,
    modification_request: str
) -> Dict[str, Any]:
    """Modify the existing plan based on user request."""
    
    # Extract current plan summary for context
    current_agents = current_plan.get("agents", [])
    current_collaboration = current_plan.get("collaboration", {})
    agent_summary = ", ".join([agent.get("name", "Unknown") for agent in current_agents])
    
    # Create enhanced modification prompt with better context
    modification_prompt = f"""You are an expert AI architecture planner modifying an existing plan based on user feedback.

CONTEXT:
Original Task: {original_task}
User's Modification Request: {modification_request}

CURRENT PLAN SUMMARY:
- Agents: {agent_summary} ({len(current_agents)} total)
- Collaboration: {"Yes" if current_collaboration.get("needed") else "No"}
- Current Approach: {current_plan.get("task_analysis", {}).get("description", "Not specified")}

FULL CURRENT PLAN:
{json.dumps(current_plan, indent=2)}

INSTRUCTIONS:
1. Carefully analyze the user's modification request
2. Understand what they want to change and why  
3. Keep what works from the current plan
4. Make targeted improvements based on their feedback
5. Ensure the modified plan is practical and implementable
6. Maintain consistency in agent roles and tool assignments

Please provide a modified JSON plan with this structure:
{{
    "task_analysis": {{
        "description": "Brief analysis of the task (updated based on modifications)",
        "complexity": "simple|medium|complex"
    }},
    "agents": [
        {{
            "name": "AgentName",
            "role": "Brief role description",
            "system_prompt": "Detailed system prompt for the agent",
            "tools": ["tool1", "tool2"],
            "tool_descriptions": {{
                "tool1": "What this tool does",
                "tool2": "What this tool does"
            }}
        }}
    ],
    "collaboration": {{
        "needed": true/false,
        "type": "sequential|parallel|hierarchical",
        "shared_memory": true/false,
        "reasoning": "Why collaboration is/isn't needed"
    }},
    "execution_flow": [
        "Step 1: Agent does X",
        "Step 2: Agent does Y"
    ]
}}

IMPORTANT: Make sure the modifications directly address the user's request while keeping the plan practical and well-structured.
"""
    
    # Get AI response
    response = SimpleAI.chat(modification_prompt, temperature=0.3)
    
    # Parse the response
    modified_plan = parse_ai_response(response, original_task)
    
    return modified_plan


def show_next_steps(plan_file: Path, project_dir: Path):
    """Show suggested next steps after planning."""
    
    next_steps_text = Text()
    next_steps_text.append("🎉 Plan Complete! Here's what to do next:\n\n", style="bold green")
    
    next_steps_text.append("STEP 1: Create your agents\n", style="bold cyan")
    next_steps_text.append("Choose one of these options:\n\n")
    
    next_steps_text.append("📦 For collaboration (multiple agents working together):\n", style="bold")
    next_steps_text.append(f"   simpleai create collaboration --from-plan {plan_file}\n\n")
    
    next_steps_text.append("🤖 For individual agents:\n", style="bold")
    next_steps_text.append(f"   simpleai create agent --from-plan {plan_file}\n\n")
    
    next_steps_text.append("STEP 2: Generate examples (optional)\n", style="bold cyan")
    next_steps_text.append(f"   simpleai generate examples --project-name {project_dir.name}\n\n")
    
    next_steps_text.append("STEP 3: Run your agents\n", style="bold cyan")
    next_steps_text.append(f"   cd {project_dir}/agents  # Go to agents directory\n")
    next_steps_text.append("   simpleai run <agent_file.py> \"Your message here\"\n\n")
    
    next_steps_text.append("📁 Your project structure:\n", style="bold cyan")
    next_steps_text.append(f"   {project_dir.name}/\n")
    next_steps_text.append(f"   ├── plan/       # Your saved plan\n")
    next_steps_text.append(f"   ├── agents/     # Created agents (coming next)\n")
    next_steps_text.append(f"   ├── examples/   # Generated examples\n")
    next_steps_text.append(f"   └── runs/       # Execution results\n\n")
    
    next_steps_text.append("💡 TIP: Use 'simpleai --help' to see all available commands", style="yellow")
    
    console.print(Panel(next_steps_text, title="🚀 What's Next?", border_style="green"))