"""
Code generators for SimpleAI CLI templates.
"""

from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from core import SimpleAI
from cli.utils import ensure_simpleai_configured
from cli.code_generation_agents import CodeGenerationTeam


def generate_ai_powered_code(
    agent_data: Dict[str, Any], 
    code_type: str, 
    additional_context: str = ""
) -> str:
    """Generate AI-powered code using 3-agent collaboration (Planner, Developer, Tester)."""
    
    try:
        # Ensure SimpleAI is configured
        ensure_simpleai_configured()
        
        print(f"🚀 Starting 3-agent collaboration for {code_type} generation...")
        
        # Create the code generation team
        code_team = CodeGenerationTeam()
        
        # Use the collaboration to generate code
        generated_code = code_team.generate_code(agent_data, code_type, additional_context)
        
        print(f"✅ Code generation collaboration completed!")
        
        return generated_code
        
    except Exception as e:
        # Fallback to single-agent generation if collaboration fails
        print(f"3-agent collaboration failed: {e}")
        print("🔄 Falling back to single-agent generation...")
        return generate_single_agent_fallback(agent_data, code_type, additional_context)


def generate_single_agent_fallback(
    agent_data: Dict[str, Any], 
    code_type: str, 
    additional_context: str = ""
) -> str:
    """Fallback to enhanced single-agent code generation."""
    
    try:
        # Ensure SimpleAI is configured
        ensure_simpleai_configured()
        
        # Load SimpleAI capabilities documentation
        capabilities_file = Path(__file__).parent.parent.parent.parent / "core/SIMPLEAI_CAPABILITIES.md"
        if capabilities_file.exists():
            with open(capabilities_file, 'r', encoding='utf-8') as f:
                capabilities_doc = f.read()
        else:
            capabilities_doc = "SimpleAI framework documentation not available."
        
        # Extract agent information
        agent_name = agent_data.get("name", "Agent")
        system_prompt = agent_data.get("system_prompt", "You are a helpful AI assistant.")
        tools_list = agent_data.get("tools", [])
        use_memory = agent_data.get("use_memory", True)
        memory_size = agent_data.get("memory_size", 20)
        
        # Build tools description
        tools_description = ""
        if tools_list:
            if isinstance(tools_list[0], dict):
                # Tools with descriptions
                tools_description = "\n".join([
                    f"- {tool.get('name', 'unknown')}: {tool.get('description', 'No description')}"
                    for tool in tools_list
                ])
            else:
                # Simple tool names
                tools_description = "\n".join([f"- {tool}: Tool for {tool.lower().replace('_', ' ')}" for tool in tools_list])
        
        # Create enhanced prompt for better code generation
        prompt = f"""You are a Senior Python Developer and AI Architect with expertise in domain-specific implementations.

FRAMEWORK DOCUMENTATION:
{capabilities_doc}

MISSION: Create a production-ready, domain-specific {code_type} implementation that solves real problems.

AGENT SPECIFICATION:
- Name: {agent_name}
- Purpose: {system_prompt}
- Required Tools: 
{tools_description if tools_description else "  Domain-appropriate tools needed"}
- Memory: {"Enabled" if use_memory else "Disabled"} ({memory_size} entries)

CONTEXT: {additional_context}

REQUIREMENTS:
1. DOMAIN-SPECIFIC: Tailor the solution to the specific use case
2. PRODUCTION-READY: No placeholders, TODOs, or generic templates
3. CREATIVE SOLUTIONS: Think innovatively about the problem
4. REAL FUNCTIONALITY: Implement actual working features
5. PROPER ARCHITECTURE: Use SimpleAI framework correctly
6. ERROR HANDLING: Include comprehensive error management
7. USER-FOCUSED: Design for real-world usage scenarios

IMPLEMENTATION APPROACH:
- Analyze the domain deeply and understand unique challenges
- Create meaningful, specific tool implementations
- Design intuitive interfaces and clear workflows
- Consider performance, scalability, and maintainability
- Include proper logging, validation, and edge case handling

GENERATE COMPLETE {code_type.upper()} CODE:
- For AGENT files: Full class with specialized tools and real implementations
- For TOOLS files: Domain-specific tools with actual functionality
- For EXAMPLES: Realistic usage scenarios that demonstrate value

Return ONLY Python code that's ready to use in production."""

        # Get AI-generated code with enhanced prompting
        response = SimpleAI.chat(prompt, temperature=0.2)  # Lower temperature for more focused output
        
        return response.strip()
        
    except Exception as e:
        # Final fallback to basic template
        print(f"Enhanced single-agent generation failed: {e}, using basic fallback")
        return generate_fallback_code(agent_data, code_type)


def generate_fallback_code(agent_data: Dict[str, Any], code_type: str) -> str:
    """Generate basic fallback code when AI generation fails."""
    
    agent_name = agent_data.get("name", "Agent")
    system_prompt = agent_data.get("system_prompt", "You are a helpful AI assistant.")
    tools_list = agent_data.get("tools", [])
    
    if code_type == "agent":
        return f'''"""
{agent_name} - AI Agent

Generated by SimpleAI CLI on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

from simpleai import SimpleAI, SimpleAgent
import os

class {agent_name}:
    """
    {agent_name} AI Agent.
    """
    
    def __init__(self):
        """Initialize the {agent_name} agent."""
        if not SimpleAI.get_config():
            raise RuntimeError("SimpleAI not configured. Please configure it first.")
        
        self.agent = SimpleAgent(
            system_prompt="""{system_prompt}""",
            tools=[],  # TODO: Implement tools
            use_memory={str(agent_data.get("use_memory", True)).lower()},
            memory_size={agent_data.get("memory_size", 20)},
            name="{agent_name}"
        )
    
    def chat(self, message: str) -> str:
        """Send a message to the agent."""
        return self.agent.chat(message)
    
    async def achat(self, message: str) -> str:
        """Send a message to the agent asynchronously."""
        return await self.agent.achat(message)

def create_agent() -> {agent_name}:
    """Create and return a {agent_name} instance."""
    return {agent_name}()

if __name__ == "__main__":
    # Configure SimpleAI
    provider = "openai" if os.getenv("OPENAI_API_KEY") else "claude"
    SimpleAI.configure(provider=provider)
    
    # Create and test the agent
    agent = create_agent()
    print(f"🤖 {agent_name} Agent Created!")
    
    response = agent.chat("Hello! What can you help me with?")
    print(f"{agent_name}: {{response}}")
'''
    
    # Add more fallback types as needed
    return f"# Fallback code for {code_type} not implemented"


def generate_agent_project(agent_data: Dict[str, Any], project_dir: Path):
    """Generate a complete agent project using smart 3-agent collaboration."""
    
    project_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Use the smart CodeGenerationTeam to create the core 3 files
        print("🤖 Using smart 3-agent team to generate agent files...")
        code_team = CodeGenerationTeam()
        
        # Generate the 3 core files (agent.py, tools.py, example_usage.py)
        success = code_team.create_agent_files(
            agent_data, 
            str(project_dir),
            additional_context="Generate a complete, working agent implementation"
        )
        
        if success:
            print("✅ Smart code generation successful!")
        else:
            raise Exception("Smart agent generation failed")
    
    except Exception as e:
        print(f"❌ Smart generation failed: {e}")
        raise e  # Don't use fallback, let it fail properly
    
    # Generate additional project files
    config_file = project_dir / "config.yaml"
    generate_config_file(agent_data, config_file)
    
    readme_file = project_dir / "README.md"
    generate_agent_readme(agent_data, readme_file)


def generate_agent_project_fallback(agent_data: Dict[str, Any], project_dir: Path):
    """Fallback agent project generation using individual file generation."""
    
    # Generate main agent file
    agent_file = project_dir / f"{agent_data['name'].lower()}_agent.py"
    generate_agent_file(agent_data, agent_file)
    
    # Generate tools file if needed
    if agent_data.get("tools"):
        tools_file = project_dir / "tools.py"
        generate_tools_file(agent_data["tools"], tools_file)
    
    # Generate example usage
    example_file = project_dir / "example_usage.py"
    generate_agent_example_file(agent_data, example_file)


def generate_collaboration_project(collab_data: Dict[str, Any], project_dir: Path):
    """Generate a complete collaboration project using smart 3-agent collaboration."""
    
    project_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Use the smart CodeGenerationTeam for collaboration generation
        print("🤖 Using smart 3-agent team to generate collaboration files...")
        code_team = CodeGenerationTeam()
        
        # First generate individual agent files using smart generation
        if "agents" in collab_data:
            agents_dir = project_dir / "agents"
            agents_dir.mkdir(exist_ok=True)
            
            for agent_name in collab_data["agents"]:
                print(f"📝 Generating agent: {agent_name}...")
                
                # Create agent data for smart generation
                agent_data = {
                    "name": agent_name,
                    "system_prompt": f"You are {agent_name}, a specialized agent in the collaboration team.",
                    "tools": [],  # Collaboration agents often use shared tools
                    "use_memory": True,
                    "memory_size": 20
                }
                
                # Generate agent files in subdirectory
                agent_dir = agents_dir / agent_name.lower()
                success = code_team.create_agent_files(
                    agent_data,
                    str(agent_dir),
                    additional_context=f"This agent is part of the {collab_data['name']} collaboration"
                )
                
                if not success:
                    raise Exception(f"Failed to generate agent {agent_name}")
        
        # Generate collaboration orchestrator file
        print("📝 Generating collaboration orchestrator...")
        collab_file = project_dir / f"{collab_data['name'].lower()}_collaboration.py"
        generate_smart_collaboration_file(collab_data, collab_file, code_team)
        
        # Generate example usage
        print("📝 Generating example usage...")
        example_file = project_dir / "example_usage.py"
        generate_smart_collaboration_example(collab_data, example_file, code_team)
        
        print("✅ Smart collaboration generation successful!")
        
    except Exception as e:
        print(f"❌ Smart generation failed: {e}")
        raise e  # Don't use fallback, let it fail properly
    
    # Always generate README
    readme_file = project_dir / "README.md"
    generate_collaboration_readme(collab_data, readme_file)


def generate_smart_collaboration_file(collab_data: Dict[str, Any], collab_file: Path, code_team: 'CodeGenerationTeam'):
    """Generate collaboration orchestrator file using smart code generation."""
    
    # Get agent details from the collaboration data
    agent_details = collab_data.get("agent_details", [])
    agent_names = collab_data.get("agents", [])
    
    # Build detailed context about the agents
    agent_context = ""
    if agent_details:
        agent_context = "AGENT DETAILS:\n"
        for agent in agent_details:
            # Handle both dict and string formats
            if isinstance(agent, dict):
                agent_context += f"- {agent.get('name', 'Agent')}: {agent.get('system_prompt', 'Helper agent')}\n"
                if agent.get('tools'):
                    agent_context += f"  Tools: {[tool.get('name', 'tool') if isinstance(tool, dict) else tool for tool in agent.get('tools', [])]}\n"
            else:
                # If agent is a string, treat it as agent name
                agent_context += f"- {agent}: Specialized agent in the collaboration\n"
    
    # Create specialized agent data for collaboration file
    collab_agent_data = {
        "name": collab_data["name"],
        "system_prompt": f"Orchestrator for multi-agent collaboration with agents: {', '.join(agent_names)}",
        "tools": [],
        "use_memory": collab_data.get("shared_memory", True),
        "memory_size": collab_data.get("memory_size", 50)
    }
    
    # Generate collaboration orchestrator code
    collab_code = code_team.generate_single_file(
        collab_agent_data,
        "collaboration orchestrator",
        "collaboration.py",
        additional_context=f"""{agent_context}

This is a SimpleCollaborate orchestrator that:
- Imports agents from agents/ subdirectory: {', '.join(agent_names)}
- Uses SimpleCollaborate to coordinate the agents
- Execution type: {collab_data.get('execution_type', 'sequential')}
- Shared memory: {collab_data.get('shared_memory', True)}
- Task description: {collab_data.get('task_description', 'Multi-agent collaboration')}

The orchestrator should create agent instances and coordinate them using SimpleCollaborate."""
    )
    
    # Write the file
    with open(collab_file, 'w', encoding='utf-8') as f:
        f.write(collab_code)


def generate_smart_collaboration_example(collab_data: Dict[str, Any], example_file: Path, code_team: 'CodeGenerationTeam'):
    """Generate collaboration example usage using smart code generation."""
    
    # Create specialized agent data for example
    example_agent_data = {
        "name": f"{collab_data['name']}Example",
        "system_prompt": f"Example usage for {collab_data['name']} collaboration",
        "tools": [],
        "use_memory": False,
        "memory_size": 0
    }
    
    # Generate example code
    example_code = code_team.generate_single_file(
        example_agent_data,
        "collaboration example",
        "example_usage.py",
        additional_context=f"""This example should:
- Import and configure SimpleAI
- Import the collaboration from {collab_data['name'].lower()}_collaboration.py
- Show realistic usage scenarios for the collaboration
- Demonstrate coordination between agents: {', '.join(collab_data['agents'])}"""
    )
    
    # Write the file
    with open(example_file, 'w', encoding='utf-8') as f:
        f.write(example_code)


def generate_agent_file(agent_data: Dict[str, Any], agent_file: Path):
    """Generate the main agent Python file using AI-powered code generation."""
    
    try:
        # Use AI to generate the agent implementation
        agent_code = generate_ai_powered_code(
            agent_data, 
            "agent", 
            "This should be a complete agent implementation with a main class, proper tool integration, and example usage."
        )
        
        # Write the generated code to file
        with open(agent_file, 'w', encoding='utf-8') as f:
            f.write(agent_code)
            
    except Exception as e:
        print(f"Failed to generate agent file: {e}")
        # Use fallback generation
        fallback_code = generate_fallback_code(agent_data, "agent")
        with open(agent_file, 'w', encoding='utf-8') as f:
            f.write(fallback_code)


def generate_tools_file(tools: List[Dict[str, Any]], tools_file: Path):
    """Generate the tools Python file using AI-powered code generation."""
    
    try:
        # Create agent data with tools for AI generation
        tools_agent_data = {
            "name": "ToolsModule",
            "tools": tools,
            "system_prompt": "Tool collection for specialized functionality"
        }
        
        # Build context about the tools
        tools_context = f"""
This should be a tools.py file containing {len(tools)} tool implementations:

Tools to implement:
"""
        for tool in tools:
            tools_context += f"- {tool.get('name', 'unknown')}: {tool.get('description', 'No description')}\n"
        
        tools_context += """
Each tool should:
1. Use the @SimpleTool decorator properly
2. Have realistic, working implementations (not just placeholders)
3. Include proper type hints and docstrings
4. Handle errors gracefully
5. Return useful results for the specific domain

Generate a complete tools.py file with all these tools implemented.
"""
        
        # Use AI to generate the tools implementation
        tools_code = generate_ai_powered_code(
            tools_agent_data, 
            "tools", 
            tools_context
        )
        
        # Write the generated code to file
        with open(tools_file, 'w', encoding='utf-8') as f:
            f.write(tools_code)
            
    except Exception as e:
        print(f"Failed to generate tools file: {e}")
        # Use fallback generation
        fallback_content = f'''"""
Tools for SimpleAI Agent

Generated by SimpleAI CLI on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

from simpleai import SimpleTool
from typing import List, Dict, Any

'''
        
        for tool in tools:
            tool_name = tool["name"]
            description = tool.get("description", f"Tool: {tool_name}")
            
            fallback_content += f'''
@SimpleTool("{description}")
def {tool_name}(query: str) -> str:
    """
    {description}
    
    Args:
        query: Input query for the tool
        
    Returns:
        Tool result as string
    """
    # TODO: Implement {tool_name} logic here
    return f"{{tool_name}} result for: {{query}}"

'''
        
        with open(tools_file, 'w', encoding='utf-8') as f:
            f.write(fallback_content)


def generate_config_file(agent_data: Dict[str, Any], config_file: Path):
    """Generate configuration YAML file."""
    
    import yaml
    
    config = {
        "agent": {
            "name": agent_data["name"],
            "system_prompt": agent_data.get("system_prompt"),
            "use_memory": agent_data.get("use_memory", True),
            "memory_size": agent_data.get("memory_size", 20),
            "tools": [tool["name"] for tool in agent_data.get("tools", [])],
        },
        "simpleai": {
            "provider": "openai",  # Default
            "model": "gpt-4o-mini",
            "temperature": 0.7,
        },
        "metadata": {
            "created_by": "SimpleAI CLI",
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
        }
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)


def generate_agent_example_file(agent_data: Dict[str, Any], example_file: Path):
    """Generate example usage file for agent using AI-powered code generation."""
    
    try:
        # Build context for example generation
        agent_name = agent_data["name"]
        system_prompt = agent_data.get("system_prompt", "")
        tools = agent_data.get("tools", [])
        
        example_context = f"""
This should be an example_usage.py file that demonstrates realistic usage of the {agent_name} agent.

Agent Details:
- Name: {agent_name}
- Purpose: {system_prompt}
- Available Tools: {[tool.get('name', 'unknown') for tool in tools]}

The example should:
1. Show realistic use cases that match the agent's purpose
2. Demonstrate the agent's tools in action
3. Include proper error handling and configuration
4. Show meaningful interactions that showcase capabilities
5. Be educational and demonstrate best practices

Generate a complete example_usage.py file with realistic scenarios.
"""
        
        # Use AI to generate the example implementation
        example_code = generate_ai_powered_code(
            agent_data, 
            "example", 
            example_context
        )
        
        # Write the generated code to file
        with open(example_file, 'w', encoding='utf-8') as f:
            f.write(example_code)
            
    except Exception as e:
        print(f"Failed to generate example file: {e}")
        # Use fallback generation
        agent_name = agent_data["name"]
        fallback_content = f'''"""
Example usage for {agent_name} Agent

This file demonstrates how to use the {agent_name} agent.
"""

import os
from simpleai import SimpleAI
from {agent_name.lower()}_agent import create_agent


def main():
    """Main example function."""
    print("🚀 {agent_name} Agent Example")
    print("=" * 40)
    
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Please set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        return
    
    # Configure SimpleAI
    provider = "openai" if os.getenv("OPENAI_API_KEY") else "claude"
    model = "gpt-4o-mini" if provider == "openai" else "claude-3-5-sonnet-20241022"
    
    print(f"🔧 Configuring SimpleAI with {{provider}} ({{model}})")
    SimpleAI.configure(provider=provider, model=model)
    
    # Create agent
    print(f"🤖 Creating {{agent_name}} agent...")
    agent = create_agent()
    
    # Example interactions
    examples = [
        "Hello! What can you help me with?",
        "Tell me about yourself",
        "What are your capabilities?",
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\\n--- Example {{i}} ---")
        print(f"User: {{example}}")
        
        try:
            response = agent.chat(example)
            print(f"{agent_name}: {{response}}")
        except Exception as e:
            print(f"❌ Error: {{e}}")
    
    # Show memory stats
    print(f"\\n--- Memory Stats ---")
    stats = agent.get_memory_stats()
    print(f"Memory entries: {{stats.get('entries', 0)}}")
    print(f"Tools used: {{stats.get('tools_used', [])}}")
    
    print(f"\\n✅ {agent_name} example completed!")


if __name__ == "__main__":
    main()
'''
        
        with open(example_file, 'w', encoding='utf-8') as f:
            f.write(fallback_content)


def generate_agent_readme(agent_data: Dict[str, Any], readme_file: Path):
    """Generate README for agent project."""
    
    agent_name = agent_data["name"]
    system_prompt = agent_data.get("system_prompt", "")
    tools = agent_data.get("tools", [])
    
    content = f'''# {agent_name} Agent

AI agent created with SimpleAI CLI.

## Description

{system_prompt}

## Features

- **Memory**: {"Enabled" if agent_data.get("use_memory") else "Disabled"}
- **Memory Size**: {agent_data.get("memory_size", 20)} entries
- **Tools**: {len(tools)} tool(s)

## Tools

{chr(10).join(f"- **{tool['name']}**: {tool.get('description', 'No description')}" for tool in tools) if tools else "No tools configured"}

## Usage

### Prerequisites

Set your API key in environment variables:

```bash
# For OpenAI
export OPENAI_API_KEY="your-openai-key"

# For Claude
export ANTHROPIC_API_KEY="your-anthropic-key"

# Or in .env file
echo "OPENAI_API_KEY=your-key" > .env
```

### Basic Usage

```python
from simpleai import SimpleAI
from {agent_name.lower()}_agent import create_agent

# Configure SimpleAI
SimpleAI.configure(provider="openai", model="gpt-4o-mini")

# Create agent
agent = create_agent()

# Chat with agent
response = agent.chat("Hello!")
print(response)
```

### Interactive Mode

```bash
python {agent_name.lower()}_agent.py
```

### Example Usage

```bash
python example_usage.py
```

## Files

- `{agent_name.lower()}_agent.py` - Main agent implementation
{f"- `tools.py` - Tool implementations" if tools else ""}
- `config.yaml` - Configuration file
- `example_usage.py` - Usage examples
- `README.md` - This file

## Generated by

SimpleAI CLI on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
'''
    
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(content)


def generate_basic_agent_file(agent_name: str, agent_file: Path):
    """Generate a basic agent file for collaborations."""
    
    content = f'''"""
{agent_name} - Basic AI Agent for Collaboration

Generated by SimpleAI CLI on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

from simpleai import SimpleAI, SimpleAgent


def create_{agent_name.lower()}_agent():
    """Create and return a {agent_name} agent."""
    
    return SimpleAgent(
        system_prompt="You are {agent_name}, a helpful AI assistant specialized in your domain.",
        tools=[],  # Add tools as needed
        use_memory=True,
        memory_size=20,
        name="{agent_name}"
    )


if __name__ == "__main__":
    # Test the agent
    import os
    
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        exit(1)
    
    provider = "openai" if os.getenv("OPENAI_API_KEY") else "claude"
    SimpleAI.configure(provider=provider)
    
    agent = create_{agent_name.lower()}_agent()
    response = agent.chat("Hello! What can you help with?")
    print(f"{agent_name}: {{response}}")
'''
    
    with open(agent_file, 'w', encoding='utf-8') as f:
        f.write(content)


def generate_collaboration_file(collab_data: Dict[str, Any], collab_file: Path):
    """Generate collaboration Python file."""
    
    collab_name = collab_data["name"]
    agents = collab_data.get("agents", [])
    shared_memory = collab_data.get("shared_memory", True)
    memory_size = collab_data.get("memory_size", 50)
    
    # Build agent imports
    agent_imports = [f"from {agent.lower()}_agent import create_{agent.lower()}_agent" for agent in agents]
    
    content = f'''"""
{collab_name} - Multi-Agent Collaboration

Generated by SimpleAI CLI on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

from simpleai import SimpleAI, SimpleCollaborate
{chr(10).join(agent_imports)}


class {collab_name}:
    """
    {collab_name} Multi-Agent Collaboration.
    
    Agents: {", ".join(agents)}
    Shared Memory: {"Enabled" if shared_memory else "Disabled"}
    Memory Size: {memory_size}
    """
    
    def __init__(self):
        """Initialize the collaboration."""
        # Ensure SimpleAI is configured
        if not SimpleAI.get_config():
            raise RuntimeError(
                "SimpleAI not configured. Please configure it first:\\n"
                "SimpleAI.configure(provider='openai', model='gpt-4o')"
            )
        
        # Create agents
        self.agents = [
{chr(10).join(f"            create_{agent.lower()}_agent()," for agent in agents)}
        ]
        
        # Create collaboration
        self.collaboration = SimpleCollaborate(
            agents=self.agents,
            shared_memory={str(shared_memory).lower()},
            memory_size={memory_size}
        )
    
    def execute(self, task: str) -> dict:
        """
        Execute a collaborative task.
        
        Args:
            task: Task description for the agents to work on
            
        Returns:
            Dictionary with execution results
        """
        return self.collaboration.execute(task)
    
    async def aexecute(self, task: str) -> dict:
        """
        Execute a collaborative task asynchronously.
        
        Args:
            task: Task description for the agents to work on
            
        Returns:
            Dictionary with execution results
        """
        return await self.collaboration.aexecute(task)
    
    def clear_memory(self):
        """Clear shared memory."""
        self.collaboration.clear_memory()
    
    def get_memory_stats(self) -> dict:
        """Get memory statistics."""
        return self.collaboration.get_memory_stats()


def create_collaboration() -> {collab_name}:
    """Create and return a {collab_name} instance."""
    return {collab_name}()


if __name__ == "__main__":
    # Example usage
    import os
    
    # Configure SimpleAI if not already configured
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        exit(1)
    
    # Configure SimpleAI
    provider = "openai" if os.getenv("OPENAI_API_KEY") else "claude"
    SimpleAI.configure(provider=provider)
    
    # Create and test the collaboration
    collaboration = create_collaboration()
    
    print(f"🤖 {collab_name} Collaboration Created!")
    print("Type 'quit' to exit, 'clear' to clear memory, or 'stats' for memory stats")
    
    while True:
        user_input = input("\\nTask: ").strip()
        
        if user_input.lower() == 'quit':
            break
        elif user_input.lower() == 'clear':
            collaboration.clear_memory()
            print("✅ Memory cleared")
            continue
        elif user_input.lower() == 'stats':
            stats = collaboration.get_memory_stats()
            print(f"📊 Memory Stats: {{stats}}")
            continue
        elif not user_input:
            continue
        
        try:
            print("🚀 Executing collaborative task...")
            result = collaboration.execute(user_input)
            
            print("\\n--- Results ---")
            for step_result in result.get('results', []):
                agent_name = step_result.get('agent', 'Unknown')
                status = step_result.get('status', 'unknown')
                output = step_result.get('output', 'No output')
                
                print(f"{{agent_name}} ({{status}}): {{output[:200]}}{{\'...\' if len(output) > 200 else \'\'}}")
                
        except Exception as e:
            print(f"❌ Error: {{e}}")
'''
    
    with open(collab_file, 'w', encoding='utf-8') as f:
        f.write(content)


def generate_collaboration_example_file(collab_data: Dict[str, Any], example_file: Path):
    """Generate example usage file for collaboration."""
    
    collab_name = collab_data["name"]
    
    content = f'''"""
Example usage for {collab_name} Collaboration

This file demonstrates how to use the {collab_name} collaboration.
"""

import os
from simpleai import SimpleAI
from {collab_name.lower()}_collaboration import create_collaboration


def main():
    """Main example function."""
    print("🚀 {collab_name} Collaboration Example")
    print("=" * 50)
    
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Please set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        return
    
    # Configure SimpleAI
    provider = "openai" if os.getenv("OPENAI_API_KEY") else "claude"
    model = "gpt-4o-mini" if provider == "openai" else "claude-3-5-sonnet-20241022"
    
    print(f"🔧 Configuring SimpleAI with {{provider}} ({{model}})")
    SimpleAI.configure(provider=provider, model=model)
    
    # Create collaboration
    print(f"🤖 Creating {{collab_name}} collaboration...")
    collaboration = create_collaboration()
    
    # Example tasks
    examples = [
        "Analyze the current market trends and provide recommendations",
        "Create a comprehensive report on artificial intelligence",
        "Develop a strategy for improving customer satisfaction",
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\\n--- Example {{i}} ---")
        print(f"Task: {{example}}")
        
        try:
            print("🚀 Executing collaborative task...")
            result = collaboration.execute(example)
            
            # Display results
            print("\\n📋 Execution Plan:")
            for step in result.get('plan', []):
                print(f"  Step {{step.get('step', '?')}}: {{step.get('agent', 'Unknown')}} - {{step.get('action', 'No action')}}")
            
            print("\\n📊 Results:")
            for step_result in result.get('results', []):
                agent_name = step_result.get('agent', 'Unknown')
                status = step_result.get('status', 'unknown')
                output = step_result.get('output', 'No output')
                
                status_emoji = "✅" if status == "success" else "❌"
                print(f"  {{status_emoji}} {{agent_name}}: {{output[:150]}}{{\'...\' if len(output) > 150 else \'\'}}")
            
        except Exception as e:
            print(f"❌ Error: {{e}}")
    
    # Show memory stats
    print(f"\\n--- Memory Stats ---")
    stats = collaboration.get_memory_stats()
    print(f"Memory entries: {{stats.get('entries', 0)}}")
    print(f"Agent contributions: {{stats.get('agent_contributions', {{}})}}")
    
    print(f"\\n✅ {collab_name} example completed!")


if __name__ == "__main__":
    main()
'''
    
    with open(example_file, 'w', encoding='utf-8') as f:
        f.write(content)


def generate_collaboration_readme(collab_data: Dict[str, Any], readme_file: Path):
    """Generate README for collaboration project."""
    
    collab_name = collab_data["name"]
    agents = collab_data.get("agents", [])
    
    content = f'''# {collab_name} Collaboration

Multi-agent collaboration created with SimpleAI CLI.

## Overview

This collaboration coordinates {len(agents)} AI agents to work together on complex tasks.

## Agents

{chr(10).join(f"- **{agent}**: Specialized AI agent" for agent in agents)}

## Features

- **Shared Memory**: {"Enabled" if collab_data.get("shared_memory") else "Disabled"}
- **Memory Size**: {collab_data.get("memory_size", 50)} entries
- **Execution Type**: {collab_data.get("execution_type", "Sequential")}
- **AI-Powered Planning**: Automatic task decomposition and agent coordination

## Usage

### Prerequisites

Set your API key in environment variables:

```bash
# For OpenAI
export OPENAI_API_KEY="your-openai-key"

# For Claude
export ANTHROPIC_API_KEY="your-anthropic-key"

# Or in .env file
echo "OPENAI_API_KEY=your-key" > .env
```

### Basic Usage

```python
from simpleai import SimpleAI
from {collab_name.lower()}_collaboration import create_collaboration

# Configure SimpleAI
SimpleAI.configure(provider="openai", model="gpt-4o-mini")

# Create collaboration
collaboration = create_collaboration()

# Execute a task
result = collaboration.execute("Your complex task here")

# View results
for step_result in result['results']:
    print(f"{{step_result['agent']}}: {{step_result['output']}}")
```

### Interactive Mode

```bash
python {collab_name.lower()}_collaboration.py
```

### Example Usage

```bash
python example_usage.py
```

## Files

- `{collab_name.lower()}_collaboration.py` - Main collaboration implementation
{chr(10).join(f"- `{agent.lower()}_agent.py` - {agent} agent implementation" for agent in agents)}
- `example_usage.py` - Usage examples
- `README.md` - This file

## How It Works

1. **Task Analysis**: The collaboration uses AI to analyze the input task
2. **Planning**: Creates an execution plan assigning work to different agents
3. **Execution**: Agents work sequentially or in parallel based on the plan
4. **Coordination**: Agents can share information through shared memory
5. **Results**: Combines outputs from all agents into a final result

## Generated by

SimpleAI CLI on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
'''
    
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(content)


def generate_tool_file(tool_data: Dict[str, Any], tool_file: Path):
    """Generate a single tool file."""
    
    tool_name = tool_data["name"]
    description = tool_data.get("description", f"Custom tool: {tool_name}")
    
    content = f'''"""
{tool_name} Tool

Generated by SimpleAI CLI on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

from simpleai import SimpleTool
from typing import Any


@SimpleTool("{description}")
def {tool_name}(input_data: str) -> str:
    """
    {description}
    
    Args:
        input_data: Input data for the tool
        
    Returns:
        Tool result as string
    """
    # TODO: Implement your tool logic here
    
    # Example implementation:
    result = f"Processed input: {{input_data}}"
    
    return result


# Example usage
if __name__ == "__main__":
    # Test the tool
    test_input = "Hello, world!"
    result = {tool_name}(test_input)
    print(f"{tool_name} result: {{result}}")
'''
    
    with open(tool_file, 'w', encoding='utf-8') as f:
        f.write(content)