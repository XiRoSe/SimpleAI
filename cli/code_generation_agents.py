"""
Code Generation Team for SimpleAI CLI

3-agent team generates working code:
- Planner: Quick architecture decisions
- Coder: Writes the actual code
- Analyst: Validates and suggests fixes
"""

from pathlib import Path
from typing import Dict, Any
import logging

from core import SimpleAgent, SimpleCollaborate
from cli.utils import ensure_simpleai_configured


logger = logging.getLogger(__name__)


class CodeGenerationTeam:
    """3-agent team for code generation."""
    
    def __init__(self):
        logger.debug("🚀 Initializing CodeGenerationTeam")
        ensure_simpleai_configured()
        
        # Load SimpleAI capabilities documentation
        logger.debug("📚 Loading SimpleAI capabilities documentation")
        self.capabilities_doc = self._load_capabilities_doc()
        logger.debug(f"📄 Loaded {len(self.capabilities_doc)} characters of documentation")
        
        # Create the 3 agents
        logger.debug("👥 Creating 3-agent team: Planner, Coder, Analyst")
        self.planner = self._create_planner()
        self.coder = self._create_coder() 
        self.analyst = self._create_analyst()
        logger.debug("✅ All agents created successfully")
        
        # Simple collaboration - Coder should be last to always generate final code
        logger.debug("🤝 Setting up agent collaboration (Planner → Analyst → Coder)")
        self.team = SimpleCollaborate(
            agents=[self.planner, self.analyst, self.coder],
            shared_memory=True,
            memory_size=20
        )
        
        self.max_iterations = 2  # Keep it simple
        logger.debug(f"⚙️  Configuration: max_iterations={self.max_iterations}")
        logger.debug("🎉 CodeGenerationTeam initialization complete")
    
    def _load_capabilities_doc(self) -> str:
        """Load SimpleAI capabilities documentation."""
        try:
            capabilities_file = Path(__file__).parent.parent.parent / "core/SIMPLEAI_CAPABILITIES.md"
            logger.debug(f"🔍 Looking for capabilities file at: {capabilities_file}")
            
            if capabilities_file.exists():
                logger.debug("✅ Capabilities file found, loading...")
                with open(capabilities_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.debug(f"📖 Successfully loaded {len(content)} characters from capabilities file")
                return content
            else:
                logger.debug("⚠️  Capabilities file not found, using fallback")
        except Exception as e:
            logger.debug(f"❌ Error loading capabilities file: {e}")
        
        # Fallback with essential framework knowledge
        fallback_doc = """SimpleAI Framework Basics:
- SimpleAgent(system_prompt, tools, use_memory, memory_size, name)
- @SimpleTool("description") for tools
- Tools take typed parameters, return strings
- SimpleAI.configure(provider, model) to setup
- agent.chat(message) and agent.achat(message) for async
- SimpleCollaborate for multi-agent workflows"""
        
        logger.debug("📋 Using fallback framework knowledge")
        return fallback_doc
    
    def _create_planner(self) -> SimpleAgent:
        """Swift architecture planner."""
        return SimpleAgent(
            system_prompt=f"""You are a swift planner. Make quick decisions about code structure.

SIMPLEAI FRAMEWORK DOCUMENTATION:
{self.capabilities_doc}

Your job: Decide what files and structure are needed.

Always plan for exactly 3 files:
1. agent.py - main agent class using SimpleAI framework
2. tools.py - agent's tools using @SimpleTool decorator
3. example_usage.py - usage example

Use the documentation above to plan proper SimpleAI usage. Be direct and specific.""",
            tools=[],
            use_memory=True,
            memory_size=10,
            name="Planner"
        )
    
    def _create_coder(self) -> SimpleAgent:
        """Agent coder - writes the actual code."""
        return SimpleAgent(
            system_prompt=f"""You are an expert Python coder who knows SimpleAI framework.

SIMPLEAI FRAMEWORK DOCUMENTATION:
{self.capabilities_doc}

CRITICAL OUTPUT FORMAT: Return ONLY the 3 Python files with file markers. NO explanations, NO markdown blocks, NO commentary.

EXACT FORMAT REQUIRED:

# agent.py
[complete Python code for agent.py - import statements, class definition, etc.]

# tools.py  
[complete Python code for tools.py - import statements, @SimpleTool decorators, functions, etc.]

# example_usage.py
[complete Python code for example_usage.py - import statements, main function, etc.]

RULES:
- Return ONLY Python code with file markers
- NO ```python blocks
- NO explanations or commentary
- NO "This implementation includes..." text
- Each file must be complete and functional
- Use proper SimpleAI framework syntax""",
            tools=[],
            use_memory=True,
            memory_size=15,
            name="Coder"
        )
    
    def _create_analyst(self) -> SimpleAgent:
        """Code analyst - validates and suggests fixes."""
        return SimpleAgent(
            system_prompt=f"""You are a code analyst specializing in SimpleAI framework code.

SIMPLEAI FRAMEWORK DOCUMENTATION:
{self.capabilities_doc}

YOUR JOB: Analyze code and provide feedback, NOT to generate code.

ANALYSIS PROCESS:
1. Review the generated code against SimpleAI documentation
2. Check for completeness and correctness
3. Verify proper SimpleAI framework usage
4. Provide specific feedback for improvement
5. Give clear verdict: GOOD, NEEDS_FIX, or MAJOR_ISSUES

NEVER generate code yourself. Only analyze and provide feedback.

Analysis criteria:
- Valid Python syntax?
- SimpleAI framework used correctly per documentation?
- Correct imports (from simpleai import SimpleAI, SimpleAgent, SimpleTool)?
- Proper SimpleAgent initialization with required parameters?
- @SimpleTool decorator used correctly?
- Code complete (not cut off)?
- All required components present?
- Any obvious bugs or framework misuse?

If NEEDS_FIX, be specific about what's wrong so the coder can fix it.
Reference the SimpleAI documentation when pointing out framework usage issues.""",
            tools=[],
            use_memory=True,
            memory_size=10,
            name="Analyst"
        )
    
    def _check_code_quality(self, code: str) -> bool:
        """Simple code quality check."""
        logger.debug("🔍 Performing code quality check")
        
        if not code or len(code) < 50:
            logger.debug(f"❌ Code too short: {len(code) if code else 0} characters")
            return False
        
        logger.debug(f"📏 Code length: {len(code)} characters")
        
        # Simple checks without AST parsing
        has_simpleai = 'from simpleai import' in code or 'import simpleai' in code
        has_class = 'class ' in code
        has_def = 'def ' in code
        
        logger.debug(f"🔍 SimpleAI import found: {has_simpleai}")
        logger.debug(f"🔍 Class definition found: {has_class}")
        logger.debug(f"🔍 Function definition found: {has_def}")
        
        # Just check for basic code structure - let AI be responsible for syntax
        result = has_simpleai and (has_class or has_def)
        logger.debug(f"🎯 Quality check result: {result}")
        return result
    
    def generate_code(self, agent_data: Dict[str, Any], code_type: str, additional_context: str = "") -> str:
        """Generate code using 3-agent team with iteration."""
        
        logger.debug(f"🚀 Starting code generation for {code_type}")
        logger.debug(f"🎯 Agent: {agent_data.get('name', 'Agent')}")
        logger.debug(f"📝 Context: {additional_context}")
        
        # Prepare task for the team
        task = f"""SIMPLEAI FRAMEWORK DOCUMENTATION:
{self.capabilities_doc}

Create {code_type} for agent: {agent_data.get('name', 'Agent')}

Agent Purpose: {agent_data.get('system_prompt', 'Helper agent')}
Tools Needed: {[tool.get('name', 'tool') for tool in agent_data.get('tools', [])]}
Context: {additional_context}

PROCESS:
1. Planner: Plan the 3-file structure (agent.py, tools.py, example_usage.py)
2. Coder: Write complete working code - RETURN ONLY CODE WITH FILE MARKERS, NO EXPLANATIONS
3. Analyst: Check if code is good or needs fixes

CRITICAL: Final output must be ONLY Python code with file markers:
# agent.py
[code]
# tools.py  
[code]
# example_usage.py
[code]

NO markdown blocks, NO explanations, NO commentary text."""

        logger.debug(f"📋 Task prepared ({len(task)} characters)")

        for iteration in range(self.max_iterations):
            logger.debug(f"🔄 Starting iteration {iteration + 1}/{self.max_iterations}")
            print(f"🔄 Iteration {iteration + 1}/{self.max_iterations}")
            
            try:
                logger.debug("👥 Executing team collaboration...")
                # Run the team collaboration
                result = self.team.execute(task)
                logger.debug(f"✅ Collaboration completed: {len(result.get('results', []))} results")
                
                logger.debug("📤 Extracting code from results...")
                # Extract code from results
                code = self._extract_code(result)
                logger.debug(f"📝 Extracted code length: {len(code) if code else 0} characters")
                
                # Quick quality check
                logger.debug("🔍 Performing quality check...")
                if self._check_code_quality(code):
                    logger.debug("🎉 Quality check passed - code generation successful!")
                    print("✅ Code generation successful!")
                    return code
                
                logger.debug("⚠️  Quality check failed, preparing improvement task...")
                # If not good enough, try again with feedback
                task = f"""IMPROVE THE CODE:

Previous attempt had issues. Generate better code.

{task}

Focus on:
- Valid Python syntax
- Complete SimpleAI framework usage
- All 3 files working properly"""
                
                logger.debug(f"🔧 Improvement task prepared for iteration {iteration + 2}")
                break
                
            except Exception as e:
                logger.debug(f"❌ Iteration {iteration + 1} failed: {e}")
                print(f"⚠️ Iteration {iteration + 1} failed: {e}")
        
        logger.debug("⏰ Max iterations reached, generation failed")
        # No fallback - let it fail properly
        raise Exception(f"Code generation failed after {self.max_iterations} iterations")
    
    def _extract_code(self, result: Dict[str, Any]) -> str:
        """Extract code from collaboration result."""
        logger.debug("📤 Extracting code from collaboration results")
        results = result.get('results', [])
        logger.debug(f"📊 Found {len(results)} results to process")
        
        for i, r in enumerate(reversed(results)):
            logger.debug(f"🔍 Processing result {len(results) - i}: status={r.get('status')}")
            
            if r.get('status') == 'success':
                output = r.get('output', '')
                logger.debug(f"📏 Output length: {len(output)} characters")
                
                # Remove any markdown code blocks first
                if '```python' in output:
                    logger.debug("🧹 Removing markdown code blocks")
                    start = output.find('```python') + 9
                    end = output.find('```', start)
                    if end > start:
                        output = output[start:end].strip()
                        logger.debug(f"✂️  Extracted from markdown: {len(output)} characters")
                
                # Remove explanatory text before file markers
                lines = output.split('\n')
                code_start = -1
                
                # Find the first file marker
                for j, line in enumerate(lines):
                    if line.strip().startswith('# agent.py') or line.strip().startswith('# tools.py') or line.strip().startswith('# example_usage.py'):
                        code_start = j
                        logger.debug(f"🎯 Found first file marker at line {j}: {line.strip()}")
                        break
                
                if code_start >= 0:
                    # Return only from the first file marker onwards
                    clean_output = '\n'.join(lines[code_start:])
                    logger.debug(f"✨ Cleaned output: {len(clean_output)} characters")
                    return clean_output
                
                # If file markers found, check if it contains Python keywords
                if any(keyword in output for keyword in ['class ', 'def ', 'import ', '# agent.py', '# tools.py']):
                    logger.debug("✅ Found Python code without proper markers")
                    return output
        
        logger.debug("❌ No valid code found in results")
        return '# No code generated'
    
    def create_agent_files(self, agent_data: Dict[str, Any], output_dir: str, additional_context: str = "") -> bool:
        """Generate and write the 3 agent files to the project directory."""
        agent_name = agent_data.get('name', 'Agent')
        logger.debug(f"🚀 Creating {agent_name} agent files in {output_dir}")
        print(f"🚀 Creating {agent_name} agent files...")
        
        # Create output directory
        output_path = Path(output_dir)
        logger.debug(f"📁 Creating output directory: {output_path}")
        output_path.mkdir(parents=True, exist_ok=True)
        logger.debug("✅ Output directory ready")
        
        # Generate each file separately with specialized prompts
        files_to_generate = [
            ("agent.py", "main agent class"),
            ("tools.py", "agent tools"), 
            ("example_usage.py", "usage example")
        ]
        
        for filename, file_type in files_to_generate:
            logger.debug(f"🎨 Generating {filename} ({file_type})...")
            print(f"📝 Generating {filename}...")
            
            try:
                # Generate code for this specific file
                file_code = self.generate_single_file(agent_data, file_type, filename, additional_context)
                
                # Write the file
                file_path = output_path / filename
                logger.debug(f"✍️  Writing {filename} ({len(file_code)} characters)")
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_code)
                
                logger.debug(f"✅ Successfully wrote {filename}")
                print(f"✅ Created: {file_path}")
                
            except Exception as e:
                logger.debug(f"❌ Failed to generate/write {filename}: {e}")
                print(f"❌ Failed to generate/write {filename}: {e}")
                return False
        
        logger.debug(f"🎉 All files created successfully in {output_dir}")
        print(f"🎉 {agent_name} agent created successfully in {output_dir}")
        return True
    
    def generate_single_file(self, agent_data: Dict[str, Any], file_type: str, filename: str, additional_context: str = "") -> str:
        """Generate a single file with specialized prompt and iteration for improvement."""
        
        agent_name = agent_data.get('name', 'Agent')
        system_prompt = agent_data.get('system_prompt', 'Helper agent')
        tools = agent_data.get('tools', [])
        use_memory = agent_data.get('use_memory', True)
        memory_size = agent_data.get('memory_size', 20)
        
        logger.debug(f"🎯 Generating {filename} with specialized prompt and iteration")
        
        # Create specialized prompts for each file type
        base_task = self._create_file_prompt(filename, agent_name, system_prompt, tools, use_memory, memory_size, additional_context)
        
        # Iterate with the 3-agent team for this specific file
        for iteration in range(self.max_iterations):
            logger.debug(f"🔄 {filename} iteration {iteration + 1}/{self.max_iterations}")
            
            try:
                if iteration == 0:
                    # First iteration - use base task with clear role separation
                    current_task = f"""{base_task}

COLLABORATION PROCESS:
1. Planner: Plan the structure and requirements for {filename}
2. Analyst: Review requirements and identify potential issues (NO CODE GENERATION)
3. Coder: Generate the complete Python code for {filename}

CRITICAL: Only the Coder generates code. The Coder must provide the final working Python code."""
                else:
                    # Subsequent iterations - include feedback and ensure coder generates final code
                    current_task = f"""IMPROVE THE {filename.upper()} FILE:

{base_task}

PREVIOUS ANALYST FEEDBACK: {feedback}

COLLABORATION PROCESS:
1. Planner: Review the feedback and plan improvements needed
2. Analyst: Summarize what needs to be fixed (NO CODE GENERATION)
3. Coder: Generate the IMPROVED, COMPLETE Python code that addresses ALL feedback

CRITICAL: Only the Coder generates code. Analyst only provides feedback.
The Coder must provide the final complete, working Python code."""
                
                logger.debug(f"👥 Running collaboration for {filename} (iteration {iteration + 1})")
                result = self.team.execute(current_task)
                
                # Extract clean code
                code = self._extract_single_file_code(result)
                
                if not code or len(code) < 50:
                    logger.debug(f"⚠️  {filename} iteration {iteration + 1}: Code too short")
                    feedback = "Generated code is too short or empty"
                    continue
                
                # Check if analyst says it's good
                analyst_feedback = self._get_analyst_feedback_from_result(result)
                if "GOOD" in analyst_feedback or "APPROVED" in analyst_feedback:
                    logger.debug(f"✅ {filename} approved after {iteration + 1} iterations")
                    return code
                elif "NEEDS_FIX" in analyst_feedback:
                    # Extract the feedback for next iteration
                    feedback = self._extract_feedback_from_analyst(analyst_feedback)
                    logger.debug(f"⚠️  {filename} needs fixes: {feedback}")
                    continue
                else:
                    # If we can't determine feedback, use basic quality check
                    if self._check_code_quality(code):
                        logger.debug(f"✅ {filename} passed quality check after {iteration + 1} iterations")
                        return code
                    else:
                        feedback = "Code quality check failed - missing basic Python structure"
                        logger.debug(f"⚠️  {filename} failed quality check")
                        continue
                        
            except Exception as e:
                logger.debug(f"❌ {filename} iteration {iteration + 1} failed: {e}")
                feedback = f"Generation failed with error: {e}"
                continue
        
        # If we get here, all iterations failed
        raise Exception(f"Failed to generate acceptable {filename} after {self.max_iterations} iterations")
    
    def _create_file_prompt(self, filename: str, agent_name: str, system_prompt: str, tools: list, use_memory: bool, memory_size: int, additional_context: str) -> str:
        """Create specialized prompt for each file type."""
        
        if filename == "agent.py":
            return f"""SIMPLEAI FRAMEWORK DOCUMENTATION:
{self.capabilities_doc}

Generate COMPLETE agent.py file for: {agent_name}

AGENT SPECIFICATIONS:
- Name: {agent_name}
- Purpose: {system_prompt}
- Tools: {[tool.get('name', 'tool') for tool in tools]}
- Memory: {"Enabled" if use_memory else "Disabled"} ({memory_size} entries)
- Context: {additional_context}

REQUIREMENTS FOR COMPLETE agent.py:
1. Import SimpleAI framework: from simpleai import SimpleAI, SimpleAgent
2. Import tools: from tools import get_tools
3. Create COMPLETE {agent_name} class
4. COMPLETE __init__ method with SimpleAgent initialization
5. COMPLETE chat(self, message: str) -> str method
6. COMPLETE create_agent() function that returns {agent_name}()
7. COMPLETE if __name__ == "__main__" section with testing

CRITICAL: Generate the ENTIRE file. Do not cut off at __init__. Include ALL methods and functions.
Return ONLY complete Python code. NO explanations, NO markdown blocks."""

        elif filename == "tools.py":
            return f"""SIMPLEAI FRAMEWORK DOCUMENTATION:
{self.capabilities_doc}

Generate COMPLETE tools.py file for: {agent_name}

AGENT SPECIFICATIONS:
- Name: {agent_name} 
- Purpose: {system_prompt}
- Tools Needed: {[tool.get('name', 'tool') for tool in tools]}
- Context: {additional_context}

REQUIREMENTS FOR COMPLETE tools.py:
1. Import SimpleTool: from simpleai import SimpleTool
2. Create {len(tools) if tools else 3} COMPLETE tools using @SimpleTool decorator
3. Each tool must have COMPLETE implementation with proper type hints
4. Tools must be relevant to: {system_prompt}
5. COMPLETE get_tools() function returning list of all tools
6. All functions must be COMPLETE, not cut off

CRITICAL: Generate the ENTIRE file with all tools fully implemented.
Return ONLY complete Python code. NO explanations, NO markdown blocks."""

        elif filename == "example_usage.py":
            return f"""SIMPLEAI FRAMEWORK DOCUMENTATION:
{self.capabilities_doc}

Generate COMPLETE example_usage.py file for: {agent_name}

AGENT SPECIFICATIONS:
- Name: {agent_name}
- Purpose: {system_prompt}
- Tools: {[tool.get('name', 'tool') for tool in tools]}
- Context: {additional_context}

REQUIREMENTS FOR COMPLETE example_usage.py:
1. Import SimpleAI: from simpleai import SimpleAI
2. Import agent: from agent import create_agent
3. COMPLETE main() function with realistic examples
4. COMPLETE SimpleAI configuration setup
5. COMPLETE error handling
6. Multiple COMPLETE interaction examples
7. COMPLETE if __name__ == "__main__" section

CRITICAL: Generate the ENTIRE file with complete examples and error handling.
Return ONLY complete Python code. NO explanations, NO markdown blocks."""

        elif filename == "collaboration.py":
            return f"""SIMPLEAI FRAMEWORK DOCUMENTATION:
{self.capabilities_doc}

Generate COMPLETE collaboration orchestrator file for: {agent_name}

COLLABORATION SPECIFICATIONS:
- Name: {agent_name}
- Purpose: {system_prompt}
- Context: {additional_context}

REQUIREMENTS FOR COMPLETE collaboration.py:
1. Import SimpleAI framework: from simpleai import SimpleAI, SimpleCollaborate
2. Import all agents from agents/ subdirectory
3. Create COMPLETE {agent_name} class with SimpleCollaborate
4. COMPLETE __init__ method that creates all agents and collaboration
5. COMPLETE execute(self, task: str) -> dict method
6. COMPLETE async aexecute(self, task: str) -> dict method
7. COMPLETE create_collaboration() function
8. COMPLETE if __name__ == "__main__" section with interactive testing

CRITICAL: Generate the ENTIRE collaboration orchestrator file.
The collaboration should coordinate multiple agents working together.
Return ONLY complete Python code. NO explanations, NO markdown blocks."""

        else:
            raise ValueError(f"Unknown file type: {filename}")
    
    def _get_analyst_feedback_from_result(self, result: Dict[str, Any]) -> str:
        """Extract analyst feedback from collaboration result."""
        results = result.get('results', [])
        
        # Look for analyst's response (usually the last one)
        for r in reversed(results):
            if r.get('agent') == 'Analyst' and r.get('status') == 'success':
                return r.get('output', '')
        
        return ''
    
    def _extract_feedback_from_analyst(self, analyst_output: str) -> str:
        """Extract specific feedback points from analyst output."""
        # Look for feedback after "NEEDS_FIX" or similar
        if "because:" in analyst_output:
            feedback_part = analyst_output.split("because:")[1]
        elif "To fix:" in analyst_output:
            feedback_part = analyst_output.split("To fix:")[1]
        else:
            feedback_part = analyst_output
        
        # Clean up and return first few key points
        lines = feedback_part.strip().split('\n')
        key_points = []
        for line in lines[:5]:  # Take first 5 points
            line = line.strip()
            if line and not line.startswith('The current'):
                key_points.append(line)
        
        return '; '.join(key_points)
    
    def _extract_single_file_code(self, result: Dict[str, Any]) -> str:
        """Extract code specifically from the Coder agent's output."""
        logger.debug("📤 Extracting code from Coder agent")
        results = result.get('results', [])
        
        # First, look specifically for the Coder agent's output
        for r in reversed(results):
            if r.get('agent') == 'Coder' and r.get('status') == 'success':
                output = r.get('output', '').strip()
                logger.debug(f"🎯 Found Coder output: {len(output)} characters")
                
                # Clean the coder's output
                cleaned_code = self._clean_code_output(output)
                if cleaned_code:
                    logger.debug(f"✨ Cleaned Coder output: {len(cleaned_code)} characters")
                    return cleaned_code
        
        # Fallback: look for any successful result with Python code
        logger.debug("⚠️  No Coder output found, trying fallback extraction")
        for r in reversed(results):
            if r.get('status') == 'success':
                output = r.get('output', '').strip()
                cleaned_code = self._clean_code_output(output)
                if cleaned_code:
                    logger.debug(f"📝 Fallback extraction successful: {len(cleaned_code)} characters")
                    return cleaned_code
        
        logger.debug("❌ No valid code found in any results")
        return ''
    
    def _clean_code_output(self, output: str) -> str:
        """Clean code output by removing markdown and explanatory text."""
        # Remove markdown blocks
        if '```python' in output:
            start = output.find('```python') + 9
            end = output.find('```', start)
            if end > start:
                output = output[start:end].strip()
        
        # Remove any file markers (since we're generating single files now)
        lines = output.split('\n')
        clean_lines = []
        
        for line in lines:
            # Skip file markers and explanatory text
            if line.strip().startswith('# agent.py') or line.strip().startswith('# tools.py') or line.strip().startswith('# example_usage.py'):
                continue
            if 'This implementation' in line or 'The code includes' in line:
                break
            clean_lines.append(line)
        
        clean_code = '\n'.join(clean_lines).strip()
        
        # Basic validation - should contain Python code
        if any(keyword in clean_code for keyword in ['import ', 'def ', 'class ', 'from ']):
            return clean_code
        
        return ''
    
    def _parse_generated_files(self, code: str, agent_name: str) -> Dict[str, str]:
        """Parse generated code and split into 3 files."""
        logger.debug(f"🔍 Parsing {len(code)} characters of generated code")
        
        files = {
            "agent.py": "",
            "tools.py": "",
            "example_usage.py": ""
        }
        
        # Look for file markers in the generated code
        lines = code.split('\n')
        logger.debug(f"📄 Processing {len(lines)} lines of code")
        
        current_file = None
        current_content = []
        file_markers_found = []
        
        for i, line in enumerate(lines):
            # Check for file markers
            if '# agent.py' in line.lower() or 'agent.py' in line:
                logger.debug(f"🎯 Found agent.py marker at line {i+1}")
                if current_file and current_content:
                    files[current_file] = '\n'.join(current_content)
                    logger.debug(f"📝 Saved {len(current_content)} lines to {current_file}")
                current_file = "agent.py"
                current_content = []
                file_markers_found.append("agent.py")
                continue
            elif '# tools.py' in line.lower() or 'tools.py' in line:
                logger.debug(f"🎯 Found tools.py marker at line {i+1}")
                if current_file and current_content:
                    files[current_file] = '\n'.join(current_content)
                    logger.debug(f"📝 Saved {len(current_content)} lines to {current_file}")
                current_file = "tools.py"
                current_content = []
                file_markers_found.append("tools.py")
                continue
            elif '# example_usage.py' in line.lower() or 'example_usage.py' in line:
                logger.debug(f"🎯 Found example_usage.py marker at line {i+1}")
                if current_file and current_content:
                    files[current_file] = '\n'.join(current_content)
                    logger.debug(f"📝 Saved {len(current_content)} lines to {current_file}")
                current_file = "example_usage.py"
                current_content = []
                file_markers_found.append("example_usage.py")
                continue
            
            # Add content to current file
            if current_file:
                current_content.append(line)
        
        # Add the last file's content
        if current_file and current_content:
            files[current_file] = '\n'.join(current_content)
            logger.debug(f"📝 Saved final {len(current_content)} lines to {current_file}")
        
        logger.debug(f"🎯 File markers found: {file_markers_found}")
        
        # Check if parsing was successful
        parsed_files = [f for f in files.values() if f.strip()]
        logger.debug(f"✅ Successfully parsed {len(parsed_files)} files")
        
        # If parsing failed, raise an error
        if not any(files.values()):
            logger.debug("❌ No files parsed from generated code")
            raise Exception("Failed to parse generated code into separate files")
        
        return files