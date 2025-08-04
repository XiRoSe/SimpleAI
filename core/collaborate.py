"""
Multi-agent collaboration framework.
"""

import json
import logging
import asyncio
from typing import List, Dict, Any, Optional, Union
from collections import deque

from .config import SimpleAI
from .agent import SimpleAgent
from .exceptions import ConfigurationError, APIError
from .utils import extract_json_from_string


logger = logging.getLogger(__name__)


class SimpleCollaborate:
    """
    Coordinate multiple agents to work together on complex tasks.
    
    Uses AI-powered planning to determine execution strategy.
    """
    
    def __init__(
        self,
        agents: List[SimpleAgent],
        shared_memory: bool = True,
        memory_size: int = 50,
        planning_model: Optional[str] = None
    ):
        """
        Initialize collaboration framework.
        
        Args:
            agents: List of SimpleAgent instances
            shared_memory: Whether agents share memory
            memory_size: Size of shared memory
            planning_model: Model to use for planning (defaults to configured model)
            
        Raises:
            ConfigurationError: If SimpleAI not configured
            ValueError: If no agents provided
        """
        if not SimpleAI.get_config():
            raise ConfigurationError("SimpleAI not configured. Call SimpleAI.configure() first.")
        
        if not agents:
            raise ValueError("At least one agent is required for collaboration")
        
        self.agents = agents
        self.shared_memory = shared_memory
        self.planning_model = planning_model
        
        # Assign names if not set
        for i, agent in enumerate(self.agents):
            if agent.name == "Agent":
                agent.name = f"Agent{i+1}"
        
        # Initialize shared memory
        self.memory: deque = deque(maxlen=memory_size) if shared_memory else deque(maxlen=0)
        
        logger.info(f"Collaboration initialized with {len(agents)} agents")
    
    def execute(self, task: str, planning_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a collaborative task.
        
        Args:
            task: Task description
            planning_prompt: Optional custom planning prompt
            
        Returns:
            Execution results including plan and outputs
        """
        logger.debug(f"Collaboration starting execution with {len(self.agents)} agents")
        logger.debug(f"Task: {task[:200]}{'...' if len(task) > 200 else ''}")
        
        # Create execution plan
        logger.debug("Creating execution plan...")
        plan = self._create_plan(task, planning_prompt)
        logger.debug(f"Created plan with {len(plan)} steps")
        
        # Execute plan
        logger.debug("Executing collaboration plan...")
        results = self._execute_plan(plan, task)
        logger.debug(f"Collaboration execution completed with {len(results)} step results")
        
        return {
            "task": task,
            "plan": plan,
            "results": results,
            "memory": list(self.memory) if self.shared_memory else []
        }
    
    async def aexecute(self, task: str, planning_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Async version of execute.
        
        Args:
            task: Task description
            planning_prompt: Optional custom planning prompt
            
        Returns:
            Execution results including plan and outputs
        """
        # Create execution plan
        plan = self._create_plan(task, planning_prompt)
        
        # Execute plan asynchronously
        results = await self._aexecute_plan(plan, task)
        
        return {
            "task": task,
            "plan": plan,
            "results": results,
            "memory": list(self.memory) if self.shared_memory else []
        }
    
    def _create_plan(self, task: str, planning_prompt: Optional[str] = None) -> List[Dict[str, Any]]:
        """Create execution plan using AI."""
        # Build agent descriptions
        agent_descriptions = []
        for agent in self.agents:
            tools_desc = []
            for tool in agent.tools:
                if hasattr(tool, 'tool_description'):
                    tools_desc.append(f"- {tool.tool_name}: {tool.tool_description}")
            
            agent_desc = f"{agent.name}:\n"
            agent_desc += f"  System Prompt: {agent.system_prompt}\n"
            if tools_desc:
                agent_desc += f"  Tools:\n" + "\n".join(f"    {t}" for t in tools_desc)
            
            agent_descriptions.append(agent_desc)
        
        # Get exact agent names for validation
        agent_names = [agent.name for agent in self.agents]
        
        # Create planning prompt
        default_prompt = f"""You are a task planner coordinating multiple AI agents.

Task: {task}

Available Agents:
{chr(10).join(agent_descriptions)}

CRITICAL: You must ONLY use these exact agent names in your plan:
{', '.join(agent_names)}

Create a step-by-step execution plan. For each step, specify:
1. Which agent should handle it
2. What the agent should do
3. Any specific instructions

Return the plan as a JSON array with this structure:
[
    {{
        "step": 1,
        "agent": "{agent_names[0]}",
        "action": "Description of what the agent should do",
        "instructions": "Specific instructions for the agent"
    }},
    ...
]

CRITICAL RULES:
- ONLY use agent names from this list: {', '.join(agent_names)}
- Do NOT create new agent names
- Do NOT use role-based names like "Researcher" or "Planner"
- Use the exact names provided above
- Create a logical sequence of steps
- Consider agent capabilities and tools"""
        
        # If custom prompt provided, enhance it with agent information
        if planning_prompt:
            enhanced_prompt = f"""{planning_prompt}

Available Agents:
{chr(10).join(agent_descriptions)}

CRITICAL: You must ONLY use these exact agent names in your plan:
{', '.join(agent_names)}

Do NOT create new agent names. Use only: {', '.join(agent_names)}"""
            prompt = enhanced_prompt
        else:
            prompt = default_prompt
        
        # Get plan from AI
        try:
            response = SimpleAI.chat(
                prompt,
                model=self.planning_model,
                temperature=0.3  # Lower temperature for planning
            )
            
            # Check if response is empty or None
            if not response or not response.strip():
                logger.warning("Planning response was empty")
                plan_json = self._create_fallback_plan(task)
            else:
                # Extract JSON plan
                plan_json = extract_json_from_string(response)
                if not plan_json:
                    # Try to parse as direct JSON
                    try:
                        plan_json = json.loads(response.strip())
                    except json.JSONDecodeError as e:
                        # Try to fix common JSON issues
                        try:
                            from .utils import _fix_json_control_chars
                            fixed_response = _fix_json_control_chars(response.strip())
                            plan_json = json.loads(fixed_response)
                            logger.debug("Fixed JSON by escaping control characters")
                        except json.JSONDecodeError as e2:
                            logger.warning(f"Failed to parse planning response as JSON: {e}")
                            logger.debug(f"Planning response was: {response[:500]}...")
                            logger.debug(f"After fixing attempt: {e2}")
                            plan_json = self._create_fallback_plan(task)
            
            # Ensure plan_json is always a list first
            if isinstance(plan_json, dict):
                # Check if it's a wrapper dict containing the actual plan
                plan_found = False
                for key, value in plan_json.items():
                    if isinstance(value, list) and value:
                        # Found a list that might be the plan
                        first_item = value[0]
                        if isinstance(first_item, dict) and 'step' in first_item and 'agent' in first_item:
                            logger.debug(f"Extracted plan from wrapper key: {key}")
                            plan_json = value
                            plan_found = True
                            break
                
                if not plan_found:
                    # If it's a single plan step, wrap it in a list
                    if 'step' in plan_json and 'agent' in plan_json:
                        plan_json = [plan_json]
                    else:
                        logger.warning("Dictionary returned but doesn't contain valid plan structure")
                        plan_json = self._create_fallback_plan(task)
            elif not isinstance(plan_json, list):
                # If it's neither dict nor list, use fallback
                logger.warning(f"Invalid plan format returned: {type(plan_json)}")
                plan_json = self._create_fallback_plan(task)
            
            # Now validate and fix agent names in the plan
            agent_names = [agent.name for agent in self.agents]
            plan_json = self._validate_and_fix_plan(plan_json, agent_names, task)
            
            return plan_json
            
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            # Fallback plan
            return self._create_fallback_plan(task)
    
    def _create_fallback_plan(self, task: str) -> List[Dict[str, Any]]:
        """Create a fallback sequential plan when AI planning fails."""
        return [
            {
                "step": i + 1,
                "agent": agent.name,
                "action": f"Handle part {i + 1} of the task: {task}",
                "instructions": task
            }
            for i, agent in enumerate(self.agents)
        ]
    
    def _validate_and_fix_plan(self, plan: Any, valid_agent_names: List[str], task: str) -> List[Dict[str, Any]]:
        """Validate and fix agent names in the plan."""
        if not isinstance(plan, list):
            logger.warning(f"Plan is not a list, got {type(plan)}")
            return self._create_fallback_plan(task)
        
        if not valid_agent_names:
            logger.error("No valid agent names provided")
            return self._create_fallback_plan(task)
        
        valid_plan = []
        agent_name_map = {name.lower(): name for name in valid_agent_names}
        agent_index = 0  # For round-robin assignment
        
        logger.debug(f"Validating plan with {len(plan)} steps against agents: {valid_agent_names}")
        
        for i, step in enumerate(plan):
            if not isinstance(step, dict):
                logger.warning(f"Step {i+1} is not a dictionary, skipping")
                continue
                
            if 'agent' not in step:
                logger.warning(f"Step {i+1} missing 'agent' field, skipping")
                continue
                
            agent_name = step['agent']
            original_agent = agent_name
            
            # Check if agent name exists exactly
            if agent_name in valid_agent_names:
                logger.debug(f"Step {i+1}: Agent '{agent_name}' found exactly")
                valid_plan.append(step)
            else:
                # Try case-insensitive matching
                agent_lower = agent_name.lower()
                if agent_lower in agent_name_map:
                    step['agent'] = agent_name_map[agent_lower]
                    logger.debug(f"Step {i+1}: Fixed agent name '{original_agent}' -> '{step['agent']}'")
                    valid_plan.append(step)
                else:
                    # Round-robin assignment to available agents
                    step['agent'] = valid_agent_names[agent_index % len(valid_agent_names)]
                    agent_index += 1
                    logger.warning(f"Step {i+1}: Agent '{original_agent}' not found, assigned to '{step['agent']}'")
                    valid_plan.append(step)
        
        # If no valid steps, create fallback plan
        if not valid_plan:
            logger.warning("No valid plan steps found, creating fallback plan")
            return self._create_fallback_plan(task)
        
        logger.info(f"Validated plan with {len(valid_plan)} steps")
        return valid_plan
    
    def _execute_plan(self, plan: List[Dict[str, Any]], original_task: str) -> List[Dict[str, Any]]:
        """Execute the plan synchronously."""
        results = []
        context = f"Original task: {original_task}\n\n"
        
        for step in plan:
            step_num = step.get("step", len(results) + 1)
            agent_name = step.get("agent", "")
            action = step.get("action", "")
            instructions = step.get("instructions", "")
            
            # Find the agent
            agent = None
            for a in self.agents:
                if a.name == agent_name:
                    agent = a
                    break
            
            if not agent:
                logger.error(f"Agent '{agent_name}' not found")
                results.append({
                    "step": step_num,
                    "agent": agent_name,
                    "status": "error",
                    "output": f"Agent '{agent_name}' not found"
                })
                continue
            
            # Build message with context
            message = f"{context}Step {step_num}: {action}\n\nInstructions: {instructions}"
            
            # Add shared memory context
            if self.shared_memory and self.memory:
                memory_context = "\n\nShared Memory:\n"
                for mem_agent, mem_output in self.memory:
                    memory_context += f"- {mem_agent}: {mem_output[:200]}...\n"
                message += memory_context
            
            try:
                # Execute with agent
                output = agent.chat(message)
                
                # Store result
                result = {
                    "step": step_num,
                    "agent": agent_name,
                    "action": action,
                    "status": "success",
                    "output": output
                }
                results.append(result)
                
                # Update shared memory
                if self.shared_memory:
                    self.memory.append((agent_name, output))
                
                # Update context for next step
                context += f"Step {step_num} ({agent_name}): {output[:200]}...\n\n"
                
                logger.info(f"Step {step_num} completed by {agent_name}")
                
            except Exception as e:
                logger.error(f"Step {step_num} failed: {e}")
                result = {
                    "step": step_num,
                    "agent": agent_name,
                    "action": action,
                    "status": "error",
                    "output": str(e)
                }
                results.append(result)
        
        return results
    
    async def _aexecute_plan(self, plan: List[Dict[str, Any]], original_task: str) -> List[Dict[str, Any]]:
        """Execute the plan asynchronously."""
        results = []
        context = f"Original task: {original_task}\n\n"
        
        # Group steps that can be executed in parallel
        parallel_groups = self._group_parallel_steps(plan)
        
        for group in parallel_groups:
            # Execute steps in parallel within each group
            group_tasks = []
            
            for step in group:
                step_num = step.get("step", len(results) + 1)
                agent_name = step.get("agent", "")
                action = step.get("action", "")
                instructions = step.get("instructions", "")
                
                # Find the agent
                agent = None
                for a in self.agents:
                    if a.name == agent_name:
                        agent = a
                        break
                
                if not agent:
                    results.append({
                        "step": step_num,
                        "agent": agent_name,
                        "status": "error",
                        "output": f"Agent '{agent_name}' not found"
                    })
                    continue
                
                # Create task for parallel execution
                task_coro = self._execute_step_async(
                    agent, step_num, agent_name, action, instructions, context
                )
                group_tasks.append(task_coro)
            
            # Execute group in parallel
            if group_tasks:
                group_results = await asyncio.gather(*group_tasks, return_exceptions=True)
                
                for result in group_results:
                    if isinstance(result, Exception):
                        logger.error(f"Async step failed: {result}")
                        results.append({
                            "step": "unknown",
                            "agent": "unknown",
                            "status": "error",
                            "output": str(result)
                        })
                    else:
                        results.append(result)
                        # Update context for next group
                        if result["status"] == "success":
                            context += f"Step {result['step']} ({result['agent']}): {result['output'][:200]}...\n\n"
                            if self.shared_memory:
                                self.memory.append((result['agent'], result['output']))
        
        return results
    
    async def _execute_step_async(
        self,
        agent: SimpleAgent,
        step_num: int,
        agent_name: str,
        action: str,
        instructions: str,
        context: str
    ) -> Dict[str, Any]:
        """Execute a single step asynchronously."""
        # Build message with context
        message = f"{context}Step {step_num}: {action}\n\nInstructions: {instructions}"
        
        # Add shared memory context
        if self.shared_memory and self.memory:
            memory_context = "\n\nShared Memory:\n"
            for mem_agent, mem_output in self.memory:
                memory_context += f"- {mem_agent}: {mem_output[:200]}...\n"
            message += memory_context
        
        try:
            # Execute with agent
            output = await agent.achat(message)
            
            logger.info(f"Step {step_num} completed by {agent_name}")
            
            return {
                "step": step_num,
                "agent": agent_name,
                "action": action,
                "status": "success",
                "output": output
            }
            
        except Exception as e:
            logger.error(f"Step {step_num} failed: {e}")
            return {
                "step": step_num,
                "agent": agent_name,
                "action": action,
                "status": "error",
                "output": str(e)
            }
    
    def _group_parallel_steps(self, plan: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Group steps that can be executed in parallel.
        
        Simple heuristic: Steps with different agents can run in parallel
        if they don't depend on each other.
        """
        if not plan:
            return []
        
        # For now, execute sequentially
        # TODO: Implement dependency analysis for true parallel execution
        return [[step] for step in plan]
    
    def clear_memory(self) -> None:
        """Clear shared memory."""
        self.memory.clear()
        logger.debug("Collaboration memory cleared")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        agent_contributions = {}
        for agent_name, _ in self.memory:
            agent_contributions[agent_name] = agent_contributions.get(agent_name, 0) + 1
        
        return {
            "entries": len(self.memory),
            "max_entries": self.memory.maxlen,
            "agent_contributions": agent_contributions
        }
    
    def __repr__(self) -> str:
        """String representation."""
        agent_names = [agent.name for agent in self.agents]
        return f"SimpleCollaborate(agents={agent_names}, shared_memory={self.shared_memory})"