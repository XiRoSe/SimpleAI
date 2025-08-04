# SimpleAI CLI Documentation

A powerful command-line interface for the SimpleAI framework that helps you plan, create, run, and generate AI agents and multi-agent collaborations.

## Installation

Install SimpleAI with CLI support:

```bash
pip install -e .
```

Or install dependencies manually:

```bash
pip install -r requirements.txt
```

## Configuration

Set your API keys in environment variables or `.env` file:

```bash
# OpenAI
export OPENAI_API_KEY="your-openai-key"

# Claude  
export ANTHROPIC_API_KEY="your-anthropic-key"

# Or in .env file
echo "OPENAI_API_KEY=your-key" > .env
echo "LOG_LEVEL=DEBUG" >> .env
```

## Commands Overview

```bash
simpleai --help                    # Show help
simpleai plan <task>               # AI-powered task planning  
simpleai create <type> <name>      # Generate agents/collaborations
simpleai run <file> <input>        # Execute agents/collaborations
simpleai generate examples         # Create example projects
```

---

## `simpleai plan` - AI-Powered Task Planning

Analyze tasks and get AI-suggested agent architectures.

### Basic Usage

```bash
simpleai plan "Create a marketing strategy for a tech startup"
```

### Options

```bash
--complexity simple|medium|complex    # Expected task complexity
--agents N                           # Preferred number of agents
--collaboration/--no-collaboration   # Force collaboration on/off
--save-plan                         # Save plan to plan.yaml
-o, --output-dir DIR                # Output directory
```

### Examples

```bash
# Basic planning
simpleai plan "Analyze customer feedback and create improvement recommendations"

# Save plan for later use
simpleai plan "Build a content creation pipeline" --save-plan

# Complex task with specific requirements
simpleai plan "Create AI-powered financial analysis system" --complexity complex --agents 5
```

### Output

- Detailed task analysis
- Recommended agents and their roles
- Required tools for each agent
- Collaboration strategy
- Estimated costs and execution time
- Next steps recommendations

---

## `simpleai create` - Generate Agents & Collaborations

Create AI agents, collaborations, and tools from templates or plans.

### Create Single Agent

```bash
simpleai create agent <name> [options]
```

#### Options

```bash
--system-prompt TEXT              # Agent's system prompt
--tools tool1,tool2               # Comma-separated tool list
--interactive                     # Interactive creation wizard
--memory/--no-memory             # Enable/disable memory
--memory-size N                  # Memory size (default: 20)
--from-plan plan.yaml            # Create from existing plan
```

#### Examples

```bash
# Basic agent
simpleai create agent WeatherBot --system-prompt "You help with weather" --tools "get_weather,get_forecast"

# Interactive creation
simpleai create agent MyBot --interactive

# From existing plan
simpleai create agent --from-plan plan.yaml
```

### Create Collaboration

```bash
simpleai create collaboration <name> [options]
```

#### Options

```bash
--agents agent1.py,agent2.py     # Agent files to include
--shared-memory/--no-shared-memory # Shared memory between agents
--memory-size N                  # Shared memory size
--from-plan plan.yaml           # Create from existing plan
```

#### Examples

```bash
# Multi-agent collaboration
simpleai create collaboration TeamWork --agents "analyst.py,writer.py,editor.py"

# From plan
simpleai create collaboration --from-plan plan.yaml
```

### Create Custom Tool

```bash
simpleai create tool <name> [options]
```

#### Examples

```bash
simpleai create tool get_weather --description "Get weather for a city"
```

---

## `simpleai run` - Execute Agents & Collaborations

Run AI agents and collaborations with input messages.

### Basic Usage

```bash
simpleai run <file> "<input_message>"
```

### Options

```bash
--save-results/--no-save-results    # Save execution results (default: true)
--format json|text|both             # Output format (default: both)
--stream/--no-stream               # Enable streaming output
--verbose/--quiet                  # Verbose execution details
```

### Examples

```bash
# Run single agent
simpleai run my_agent.py "Hello, how can you help me?"

# Run collaboration with verbose output
simpleai run team_collaboration.py "Analyze Q4 sales data" --verbose

# Save results in JSON only
simpleai run agent.py "Your message" --format json

# Quiet execution without saving
simpleai run bot.py "Quick question" --quiet --no-save-results
```

### Output

- Real-time execution progress
- Agent/collaboration responses
- Memory statistics (if verbose)
- Execution metadata
- Saved results in `outputs/runs/` (if enabled)

---

## `simpleai generate` - Create Examples & Templates

Generate example projects and templates for learning and development.

### Generate Examples

```bash
simpleai generate examples [options]
```

#### Options

```bash
--type TYPE                      # Specific example types (multiple allowed)
--all                           # Generate all available examples
```

#### Available Example Types

- `basic_agent` - Simple single-agent
- `weather_bot` - Agent with weather tools
- `customer_service` - Multi-tool support agent
- `data_analysis` - Data analysis collaboration
- `content_creation` - Content generation team
- `research_assistant` - Comprehensive research agent
- `multi_agent_team` - Complex collaboration

#### Examples

```bash
# Generate specific examples
simpleai generate examples --type basic_agent --type weather_bot

# Generate all examples
simpleai generate examples --all

# Interactive selection
simpleai generate examples
```

### Generate Project Template

```bash
simpleai generate project <name> [options]
```

#### Options

```bash
--template TYPE                  # Project template type
--interactive                   # Interactive project setup
```

#### Available Templates

- `basic_agent` - Simple agent project
- `tool_agent` - Agent with custom tools
- `collaboration` - Multi-agent collaboration
- `research_team` - Research team setup

#### Examples

```bash
# Generate from template
simpleai generate project MyBot --template basic_agent

# Interactive project creation
simpleai generate project TeamProject --interactive
```

---

## Output Directory Structure

```
outputs/
├── runs/                         # Execution results
│   ├── run_2024-01-15-14-30-45/
│   │   ├── execution_result.json
│   │   ├── result.json
│   │   ├── result.txt
│   │   └── metadata.json
│   └── ...
├── projects/                     # Created projects
│   ├── WeatherBot/
│   │   ├── weather_bot_agent.py
│   │   ├── tools.py
│   │   ├── config.yaml
│   │   ├── example_usage.py
│   │   └── README.md
│   └── ...
├── examples/                     # Generated examples
│   ├── basic_agent/
│   ├── weather_bot/
│   └── ...
├── tools/                        # Custom tools
└── plan.yaml                     # Saved plans
```

---

## Complete Workflow Examples

### 1. Create a Weather Assistant

```bash
# Step 1: Plan the task
simpleai plan "Create a weather assistant that can provide current weather and forecasts" --save-plan

# Step 2: Create the agent from the plan
simpleai create agent --from-plan plan.yaml

# Step 3: Run the agent
simpleai run outputs/projects/WeatherBot/weather_bot_agent.py "What's the weather in Tokyo?"
```

### 2. Build a Content Creation Team

```bash
# Step 1: Plan a complex collaboration
simpleai plan "Create a team that researches topics, writes articles, and optimizes for SEO" --complexity complex --save-plan

# Step 2: Create the collaboration
simpleai create collaboration --from-plan plan.yaml

# Step 3: Execute the collaboration
simpleai run outputs/projects/ContentTeam/content_team_collaboration.py "Write an article about AI in healthcare"
```

### 3. Quick Agent Development

```bash
# Interactive agent creation
simpleai create agent MyBot --interactive

# Test the agent
simpleai run outputs/projects/MyBot/mybot_agent.py "Hello!"

# Generate examples for reference
simpleai generate examples --type customer_service --type research_assistant
```

---

## Configuration Files

### Global Configuration

Create `simpleai.yaml` for default settings:

```yaml
default:
  provider: openai
  model: gpt-4o-mini
  output_dir: outputs
  
logging:
  level: INFO
  
templates:
  custom_dir: ~/.simpleai/templates
```

### Agent Configuration

Generated agents include `config.yaml`:

```yaml
agent:
  name: WeatherBot
  system_prompt: "You are a weather assistant..."
  use_memory: true
  memory_size: 20
  tools: [get_weather, get_forecast]

simpleai:
  provider: openai
  model: gpt-4o-mini
  temperature: 0.7
```

---

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```bash
   # Set API key
   export OPENAI_API_KEY="your-key"
   # Or create .env file
   echo "OPENAI_API_KEY=your-key" > .env
   ```

2. **Module Import Errors**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   # Or install in development mode
   pip install -e .
   ```

3. **Permission Errors**
   ```bash
   # Check output directory permissions
   chmod 755 outputs/
   ```

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
# Or in .env file
echo "LOG_LEVEL=DEBUG" >> .env
```

### Verbose Output

Use `--verbose` flag for detailed execution information:

```bash
simpleai plan "Your task" --verbose
simpleai run agent.py "Input" --verbose
```

---

## Tips and Best Practices

### 1. Planning First
Always start with `simpleai plan` for complex tasks to get AI-powered architecture suggestions.

### 2. Use Examples
Generate examples to learn patterns and best practices:
```bash
simpleai generate examples --all
```

### 3. Iterative Development
1. Plan → Create → Test → Refine
2. Use `--save-plan` to preserve good architectures
3. Test with simple inputs first

### 4. Memory Management
- Enable memory for conversational agents
- Use larger memory for collaborations
- Clear memory when switching contexts

### 5. Tool Development
- Start with simple tools
- Test tools independently
- Use descriptive tool names and descriptions

---

## Integration with Development Workflow

### CI/CD Integration

```bash
# Test agents in CI
simpleai run agent.py "test input" --format json --no-save-results

# Generate documentation examples
simpleai generate examples --type basic_agent
```

### Development Scripts

```bash
#!/bin/bash
# dev-setup.sh
simpleai generate project MyProject --template basic_agent
cd outputs/projects/MyProject
python example_usage.py
```

---

For more information, see the main [README.md](../README.md) and explore the generated examples.