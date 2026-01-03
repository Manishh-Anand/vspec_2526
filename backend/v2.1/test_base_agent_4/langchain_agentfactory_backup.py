#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MetaFlow Agent Factory - Enhanced LangChain Implementation
Production-ready version with robust error handling and compatibility fixes

Key Enhancements:
- Stricter prompt engineering for consistent output
- Robust Claude Code output parsing  
- Tool validation before execution
- Better error messages for agent self-correction
- Retry logic with exponential backoff
- Comprehensive logging
"""

import json
import subprocess
import asyncio
import logging
import re
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# LangChain imports
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPToolInput(BaseModel):
    """
    Schema for MCP tool input with strict validation
    
    This ensures the agent provides properly formatted tool calls
    """
    tool_name: str = Field(
        description="The EXACT name of the MCP tool to execute (must match available tools exactly)"
    )
    parameters: Dict[str, Any] = Field(
        description="Parameters to pass to the tool as a JSON dictionary",
        default_factory=dict
    )
    
    @validator('tool_name')
    def tool_name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('tool_name cannot be empty')
        return v.strip()
    
    @validator('parameters')
    def parameters_must_be_dict(cls, v):
        if not isinstance(v, dict):
            raise ValueError('parameters must be a dictionary')
        return v


class ClaudeMCPTool(BaseTool):
    """
    Enhanced Universal MCP Tool Wrapper for Claude Code
    
    Improvements:
    - Tool name validation against available tools
    - Robust output parsing from Claude
    - Better error messages
    - Retry logic
    - Timeout handling
    """
    
    name: str = "mcp_tool_executor"
    description: str = """Execute MCP tools via Claude Code. This is the ONLY tool you can use.

CRITICAL: You MUST provide input in EXACT JSON format:
{{"tool_name": "exact_tool_name", "parameters": {{"param1": "value1", "param2": "value2"}}}}

Available MCP tools will be specified in your system prompt.

Examples of CORRECT usage:
{{"tool_name": "send_email", "parameters": {{"to": "user@example.com", "subject": "Hello", "body": "Message"}}}}
{{"tool_name": "search_web", "parameters": {{"query": "KTM Duke 390 price"}}}}
{{"tool_name": "create_event", "parameters": {{"title": "Meeting", "date": "2024-01-20", "time": "14:00"}}}}

DO NOT use natural language in Action Input.
DO NOT omit the parameters dictionary, even if empty: {{"tool_name": "tool", "parameters": {{}}}}
"""
    
    args_schema: type[BaseModel] = MCPToolInput
    claude_cwd: Path = Field(default_factory=lambda: Path(r"C:\Users\manis"))
    timeout: int = Field(default=300)
    max_retries: int = Field(default=2)
    available_tools: List[str] = Field(default_factory=list)
    
    def _run(self, tool_name: str = None, parameters: Dict[str, Any] = None, **kwargs) -> str:
        """
        Execute MCP tool with validation and error handling
        
        Args:
            tool_name: Name of the MCP tool to execute
            parameters: Dictionary of parameters for the tool
            **kwargs: Additional arguments (LangChain compatibility)
            
        Returns:
            Structured result string for agent consumption
        """
        # DEBUG: Log what we received
        logger.info(f"🔍 _run received tool_name: '{tool_name}'")
        logger.info(f"🔍 _run received parameters: '{parameters}'")
        logger.info(f"🔍 _run received kwargs: '{kwargs}'")
        
        # CRITICAL FIX: LangChain sometimes passes entire JSON as tool_name
        if tool_name and isinstance(tool_name, str) and tool_name.strip().startswith('{'):
            try:
                # Try to parse as JSON
                parsed = json.loads(tool_name)
                if 'tool_name' in parsed:
                    logger.info(f"   ✅ Parsed JSON from tool_name argument")
                    parameters = parsed.get('parameters', {})
                    tool_name = parsed['tool_name']
            except json.JSONDecodeError as e:
                logger.warning(f"   ⚠️  Failed to parse tool_name as JSON: {e}")
                # Try to extract from malformed JSON
                if '"tool_name":' in tool_name:
                    import re
                    match = re.search(r'"tool_name":\s*"([^"]+)"', tool_name)
                    if match:
                        actual_tool_name = match.group(1)
                        logger.info(f"   ✅ Extracted tool_name via regex: {actual_tool_name}")
                        tool_name = actual_tool_name
                    # Try to extract parameters
                    match_params = re.search(r'"parameters":\s*({[^}]+})', tool_name)
                    if match_params:
                        try:
                            parameters = json.loads(match_params.group(1))
                            logger.info(f"   ✅ Extracted parameters via regex")
                        except:
                            pass
        
        # Handle different ways LangChain might call this
        if tool_name is None and 'tool_name' in kwargs:
            tool_name = kwargs['tool_name']
        if parameters is None and 'parameters' in kwargs:
            parameters = kwargs['parameters']
        
        # Validate we have required arguments
        if tool_name is None:
            return "ERROR: tool_name is required"
        if parameters is None:
            parameters = {}
        try:
            logger.info(f"🔧 Executing MCP tool: {tool_name}")
            logger.info(f"   Parameters: {parameters}")
            
            # Validate tool name
            validation_error = self._validate_tool_name(tool_name)
            if validation_error:
                return validation_error
            
            # Execute with retry logic
            for attempt in range(self.max_retries + 1):
                try:
                    # Build Claude prompt
                    prompt = self._build_claude_prompt(tool_name, parameters)
                    
                    # Execute via subprocess
                    raw_output = self._execute_claude_command(prompt)
                    
                    # Parse output
                    parsed_result = self._parse_claude_output(raw_output, tool_name)
                    
                    logger.info(f"✅ Tool execution completed: {tool_name}")
                    logger.info(f"   Status: {parsed_result['status']}")
                    
                    return self._format_result_for_agent(parsed_result)
                    
                except subprocess.TimeoutExpired:
                    if attempt < self.max_retries:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(f"⏱️  Timeout on attempt {attempt + 1}, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        return self._format_error_for_agent(
                            tool_name,
                            "Tool execution timed out after multiple attempts",
                            "Try with simpler parameters or a different tool"
                        )
                
                except Exception as e:
                    if attempt < self.max_retries:
                        wait_time = 2 ** attempt
                        logger.warning(f"⚠️  Error on attempt {attempt + 1}: {e}, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        return self._format_error_for_agent(
                            tool_name,
                            str(e),
                            "Check if Claude Code is running and MCP servers are configured"
                        )
            
        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return self._format_error_for_agent(tool_name, str(e), "Verify tool name and parameters")
    
    async def _arun(self, tool_name: str = None, parameters: Dict[str, Any] = None, **kwargs) -> str:
        """Async version - runs sync version in executor"""
        # Handle different ways LangChain might call this
        if tool_name is None and 'tool_name' in kwargs:
            tool_name = kwargs['tool_name']
        if parameters is None and 'parameters' in kwargs:
            parameters = kwargs['parameters']
        
        return await asyncio.get_event_loop().run_in_executor(
            None, 
            self._run, 
            tool_name, 
            parameters
        )
    
    def _validate_tool_name(self, tool_name: str) -> Optional[str]:
        """
        Validate that the tool name exists in available tools
        
        Returns:
            Error message if invalid, None if valid
        """
        if not self.available_tools:
            # No validation list provided, skip validation
            return None
        
        if tool_name not in self.available_tools:
            # Check for close matches
            close_matches = [t for t in self.available_tools if tool_name.lower() in t.lower() or t.lower() in tool_name.lower()]
            
            error_msg = f"""ERROR: Tool '{tool_name}' is not available.

Available tools: {', '.join(self.available_tools)}"""
            
            if close_matches:
                error_msg += f"\n\nDid you mean one of these?\n- " + "\n- ".join(close_matches)
            
            error_msg += "\n\nPlease use the EXACT tool name from the available tools list."
            
            logger.warning(f"⚠️  Invalid tool name: {tool_name}")
            return error_msg
        
        return None
    
    def _build_claude_prompt(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """
        Build clear, explicit natural language prompt for Claude Code
        
        Claude Code works best with natural language instructions
        """
        # CRITICAL FIX: Strip MCP prefix - Claude Code doesn't understand these
        # Tool Mapper adds prefixes like "mcp__notionMCP__notion-search"
        # But Claude Code expects just "notion-search"
        original_tool_name = tool_name
        if tool_name.startswith("mcp__"):
            parts = tool_name.split("__")
            if len(parts) >= 3:
                tool_name = parts[2]  # Extract actual tool name
                logger.info(f"   🔧 Stripped MCP prefix: '{original_tool_name}' → '{tool_name}'")
            elif len(parts) == 2:
                tool_name = parts[1]  # Fallback for simpler prefixes
                logger.info(f"   🔧 Stripped MCP prefix: '{original_tool_name}' → '{tool_name}'")
        
        # Format parameters as readable text
        if parameters:
            param_parts = []
            for key, value in parameters.items():
                if isinstance(value, str):
                    param_parts.append(f"{key}: '{value}'")
                else:
                    param_parts.append(f"{key}: {value}")
            param_str = ", ".join(param_parts)
        else:
            param_str = "no parameters"
        
        # Create explicit prompt
        prompt = f"""Execute the MCP tool: {tool_name}

Parameters: {param_str}

Please execute this tool and provide a clear, concise result.
Focus on the outcome - what was accomplished or what error occurred.
"""
        
        return prompt
    
    def _execute_claude_command(self, prompt: str) -> str:
        """
        Execute Claude Code command via PowerShell subprocess
        
        Args:
            prompt: Natural language prompt for Claude
            
        Returns:
            Raw output from Claude Code
        """
        # Write prompt to temporary input file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        input_file = self.claude_cwd / f"mcp_input_{timestamp}.txt"
        
        try:
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            
            # Prepare PowerShell command
            cmd = [
                "powershell.exe",
                "-NoLogo",
                "-NoProfile",
                "-Command",
                "claude"
            ]
            
            # Execute Claude Code
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.claude_cwd),
                text=True,
                encoding='utf-8'
            )
            
            # Read input and send to Claude
            with open(input_file, 'r', encoding='utf-8') as f:
                input_data = f.read()
            
            stdout, stderr = proc.communicate(input=input_data, timeout=self.timeout)
            
            if stderr:
                logger.warning(f"Claude stderr: {stderr}")
            
            return stdout.strip()
            
        except subprocess.TimeoutExpired:
            proc.kill()
            raise
            
        except Exception as e:
            raise Exception(f"Failed to execute Claude command: {str(e)}")
            
        finally:
            # Clean up input file
            if input_file.exists():
                try:
                    input_file.unlink()
                except:
                    pass
    
    def _parse_claude_output(self, raw_output: str, tool_name: str) -> Dict[str, Any]:
        """
        Parse Claude's verbose output to extract clean result
        
        Claude often includes thinking process and commentary.
        We need to extract just the actual result.
        
        Returns:
            Dictionary with status, result, and raw output
        """
        if not raw_output or not raw_output.strip():
            return {
                "status": "error",
                "result": "Empty response from Claude Code",
                "raw": raw_output
            }
        
        # Detect status from output
        status = "unknown"
        lower_output = raw_output.lower()
        
        # Success indicators
        if any(indicator in lower_output for indicator in [
            "successfully", "✓", "✔", "completed", "sent", "created", "done"
        ]):
            status = "success"
        
        # Error indicators
        elif any(indicator in lower_output for indicator in [
            "error", "failed", "failure", "couldn't", "cannot", "unable", "❌", "✗"
        ]):
            status = "error"
        
        # Warning indicators
        elif any(indicator in lower_output for indicator in [
            "warning", "⚠", "caution"
        ]):
            status = "warning"
        
        # Extract clean result (remove Claude's meta-commentary)
        lines = raw_output.split('\n')
        
        # Filter out meta-commentary lines
        result_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Skip Claude's thinking process markers
            if line.startswith('[') or line.startswith('('):
                continue
            # Skip questions Claude asks
            if '?' in line and any(q in line.lower() for q in ['can i help', 'anything else', 'would you like']):
                continue
            result_lines.append(line)
        
        clean_result = '\n'.join(result_lines) if result_lines else raw_output
        
        return {
            "status": status,
            "result": clean_result,
            "tool": tool_name,
            "raw": raw_output
        }
    
    def _format_result_for_agent(self, parsed_result: Dict[str, Any]) -> str:
        """
        Format tool result in a way that's easy for the agent to understand
        
        The agent needs clear success/failure indication and the actual result
        """
        status = parsed_result['status']
        result = parsed_result['result']
        tool = parsed_result['tool']
        
        if status == "success":
            return f"""Tool '{tool}' executed successfully.

Result:
{result}

You can now proceed with the next step or provide a Final Answer."""
        
        elif status == "error":
            return f"""Tool '{tool}' execution failed.

Error:
{result}

Suggestion: Review the error and try again with corrected parameters, or use a different approach."""
        
        elif status == "warning":
            return f"""Tool '{tool}' executed with warnings.

Result:
{result}

Consider if this result is sufficient or if you need to retry."""
        
        else:
            return f"""Tool '{tool}' executed.

Result:
{result}"""
    
    def _format_error_for_agent(self, tool_name: str, error: str, suggestion: str) -> str:
        """
        Format error message to help agent self-correct
        
        Provides context about what went wrong and how to fix it
        """
        return f"""ERROR: Tool execution failed

Tool: {tool_name}
Error: {error}

Suggestion: {suggestion}

Available tools: {', '.join(self.available_tools) if self.available_tools else 'See your system prompt'}

Please try again with:
1. The EXACT tool name from available tools
2. All required parameters in correct format
3. Valid parameter values"""


class LangChainAgentFactory:
    """
    Enhanced Factory for creating LangChain agents from BA_enhanced.json
    
    Improvements:
    - Stricter prompt templates
    - Tool validation setup
    - Better error handling configuration
    - Comprehensive examples in prompts
    """
    
    def __init__(
        self, 
        lm_studio_url: str = "http://localhost:1234/v1",
        lm_studio_model: str = "qwen2.5-coder-14b-instruct",
        claude_cwd: Path = None
    ):
        """
        Initialize the Enhanced Agent Factory
        
        Args:
            lm_studio_url: LM Studio API endpoint
            lm_studio_model: Model identifier in LM Studio
            claude_cwd: Working directory for Claude Code
        """
        self.lm_studio_url = lm_studio_url
        self.lm_studio_model = lm_studio_model
        self.claude_cwd = claude_cwd or Path(r"C:\Users\manis")
        
        # Initialize local LLM connection (Qwen via LM Studio)
        self.llm = ChatOpenAI(
            base_url=self.lm_studio_url,
            model=self.lm_studio_model,
            api_key="not-needed",
            temperature=0.7,
            max_tokens=2000,
            request_timeout=60
        )
        
        # MCP tool will be created per-agent with tool list
        
        logger.info(f"✅ Enhanced Agent Factory initialized")
        logger.info(f"   LLM: {self.lm_studio_model} @ {self.lm_studio_url}")
        logger.info(f"   Claude Code: {self.claude_cwd}")
    
    def create_agent_from_config(self, agent_config: Dict[str, Any]) -> AgentExecutor:
        """
        Create a LangChain ReAct agent from BA_enhanced.json configuration
        
        Enhanced with:
        - Stricter prompts
        - Tool validation
        - Better error handling
        
        Args:
            agent_config: Agent configuration dictionary from BA_enhanced.json
            
        Returns:
            Configured AgentExecutor ready to run
        """
        agent_id = agent_config['agent_id']
        agent_name = agent_config['agent_name']
        
        logger.info(f"🏭 Creating enhanced agent: {agent_name} (ID: {agent_id})")
        
        # Extract tool names for validation
        tool_names = [tool['name'] for tool in agent_config['tools']]
        
        # Create MCP tool with validation
        mcp_tool = ClaudeMCPTool(
            claude_cwd=self.claude_cwd,
            available_tools=tool_names  # Enable validation
        )
        
        # Build enhanced agent-specific prompt
        prompt = self._build_enhanced_agent_prompt(agent_config)
        
        # Create ReAct agent
        agent = create_react_agent(
            llm=self.llm,
            tools=[mcp_tool],
            prompt=prompt
        )
        
        # Wrap in AgentExecutor with enhanced configuration
        agent_executor = AgentExecutor(
            agent=agent,
            tools=[mcp_tool],
            verbose=True,
            max_iterations=10,
            max_execution_time=300,  # 5 minute timeout
            handle_parsing_errors=True,
            return_intermediate_steps=True,
            early_stopping_method="generate"  # Generate answer if stuck
        )
        
        # Attach metadata for workflow builder
        agent_executor.metadata = {
            'agent_id': agent_id,
            'agent_name': agent_name,
            'position': agent_config['position'],
            'dependencies': agent_config['interface']['dependencies'],
            'outputs_to': agent_config['interface']['outputs_to'],
            'tools': agent_config['tools'],
            'tool_names': tool_names
        }
        
        logger.info(f"✅ Enhanced agent created: {agent_name}")
        logger.info(f"   Tools available: {', '.join(tool_names)}")
        logger.info(f"   Max iterations: 10")
        logger.info(f"   Timeout: 300s")
        
        return agent_executor
    
    def _build_enhanced_agent_prompt(self, agent_config: Dict[str, Any]) -> PromptTemplate:
        """
        Build STRICT ReAct prompt template with explicit formatting requirements
        
        The prompt includes:
        - Crystal clear role definition
        - Exact tool list with descriptions
        - STRICT format requirements with examples
        - Error handling guidance
        - Success criteria
        """
        agent_name = agent_config['agent_name']
        role = agent_config['identity']['role']
        description = agent_config['identity']['description']
        
        # Build detailed tool list
        tool_list = []
        for tool in agent_config['tools']:
            tool_desc = f"  • {tool['name']}: {tool.get('description', 'MCP tool')}"
            tool_list.append(tool_desc)
        
        tools_text = "\n".join(tool_list)
        tool_names = [tool['name'] for tool in agent_config['tools']]
        
        # Create STRICT ReAct prompt template with concrete examples
        # NOTE: Quadruple braces {{{{ }}}} are needed for JSON examples in f-strings
        # to result in double braces {{ }} for LangChain, which then become single braces { } for LLM
        template = f"""You are {agent_name}, a specialized AI agent in a multi-agent workflow.

ROLE:
{role}

DESCRIPTION:
{description}

YOUR AVAILABLE TOOLS (via MCP):
{tools_text}

═══════════════════════════════════════════════════════════════════════
CRITICAL FORMAT REQUIREMENTS - YOU MUST FOLLOW THIS EXACTLY:
═══════════════════════════════════════════════════════════════════════

You MUST respond using the ReAct (Reasoning and Acting) format:

Thought: [Your reasoning about what to do next]
Action: mcp_tool_executor
Action Input: {{{{"tool_name": "exact_tool_name", "parameters": {{{{"param1": "value1", "param2": "value2"}}}}}}}}
Observation: [Tool result will appear here]
... (repeat Thought/Action/Observation as needed)
Thought: [Final reasoning]
Final Answer: [Your conclusive response]

RULES:
1. Action Input MUST be valid JSON with "tool_name" and "parameters" keys
2. tool_name MUST be one of: {', '.join(tool_names)}
3. parameters MUST be a dictionary (even if empty: {{{{{{{{}}}}}}}})
4. DO NOT use natural language in Action Input
5. DO NOT add extra text after Action Input
6. DO NOT use markdown or code blocks in Action Input

═══════════════════════════════════════════════════════════════════════
CONCRETE EXAMPLES:
═══════════════════════════════════════════════════════════════════════

Example 1 - Web Search:
Thought: I need to search for information about KTM Duke 390 pricing
Action: mcp_tool_executor
Action Input: {{{{"tool_name": "search_web", "parameters": {{{{"query": "KTM Duke 390 price India 2024"}}}}}}}}
Observation: [Search results show price around ₹2.5 lakhs]
Thought: I have found the pricing information
Final Answer: The KTM Duke 390 is priced at approximately ₹2.5 lakhs in India.

Example 2 - Send Email:
Thought: I need to send an email with the research results
Action: mcp_tool_executor
Action Input: {{{{"tool_name": "send_email", "parameters": {{{{"to": "user@example.com", "subject": "KTM Research Results", "body": "The KTM Duke 390 is priced at ₹2.5 lakhs."}}}}}}}}
Observation: [Email sent successfully]
Thought: Email has been sent successfully
Final Answer: I have sent the email with KTM Duke 390 pricing information.

Example 3 - Create Calendar Event:
Thought: I need to schedule a test ride appointment
Action: mcp_tool_executor
Action Input: {{{{"tool_name": "create_event", "parameters": {{{{"title": "KTM Test Ride", "date": "2024-01-25", "time": "14:00", "description": "Test ride for KTM Duke 390"}}}}}}}}
Observation: [Event created successfully]
Thought: The test ride has been scheduled
Final Answer: I have scheduled a KTM test ride for January 25, 2024 at 2:00 PM.

═══════════════════════════════════════════════════════════════════════
ERROR HANDLING:
═══════════════════════════════════════════════════════════════════════

If a tool execution fails:
1. Read the error message carefully
2. Check if you used the correct tool name
3. Verify all required parameters are provided
4. Try again with corrected input OR use a different approach

If you're unsure, it's better to ask in your Final Answer than to make incorrect assumptions.

═══════════════════════════════════════════════════════════════════════
BEGIN:
═══════════════════════════════════════════════════════════════════════

Previous conversation:
{{chat_history}}

Current task: {{input}}

SYSTEM EXECUTION TOOL:
{{tools}}

(Tool names: {{tool_names}})

{{agent_scratchpad}}"""
        
        return PromptTemplate(
            template=template,
            input_variables=["input", "agent_scratchpad", "chat_history", "tools", "tool_names"]
        )
    
    def create_all_agents(self, ba_enhanced_path: str) -> Dict[str, AgentExecutor]:
        """
        Create all enhanced agents from BA_enhanced.json
        
        Args:
            ba_enhanced_path: Path to BA_enhanced.json file
            
        Returns:
            Dictionary mapping agent_id to AgentExecutor
        """
        logger.info(f"📄 Loading workflow from: {ba_enhanced_path}")
        
        with open(ba_enhanced_path, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        
        workflow_id = workflow_data['workflow_metadata']['workflow_id']
        domain = workflow_data['workflow_metadata']['domain']
        
        logger.info(f"🎯 Workflow: {workflow_id}")
        logger.info(f"   Domain: {domain}")
        logger.info(f"   Total agents: {workflow_data['workflow_metadata']['total_agents']}")
        
        # Create each agent with enhanced configuration
        agents = {}
        for agent_config in workflow_data['agents']:
            try:
                agent_executor = self.create_agent_from_config(agent_config)
                agents[agent_config['agent_id']] = agent_executor
            except Exception as e:
                logger.error(f"❌ Failed to create agent {agent_config['agent_id']}: {e}")
                raise
        
        logger.info(f"✅ Created {len(agents)} enhanced agents successfully")
        
        return agents
    
    def test_agent(self, agent: AgentExecutor, test_input: str) -> Dict[str, Any]:
        """
        Test an individual agent with sample input
        
        Args:
            agent: AgentExecutor to test
            test_input: Test input string
            
        Returns:
            Agent execution result with detailed logging
        """
        logger.info(f"🧪 Testing agent: {agent.metadata['agent_name']}")
        logger.info(f"   Input: {test_input}")
        
        try:
            start_time = time.time()
            
            result = agent.invoke({
                "input": test_input,
                "chat_history": ""
            })
            
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"✅ Test completed in {duration:.2f}s")
            logger.info(f"   Output: {result.get('output', 'No output')[:100]}...")
            
            return {
                "success": True,
                "duration": duration,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def main():
    """
    Example usage and testing
    """
    import sys
    
    if len(sys.argv) < 2:
        print("\n🏭 MetaFlow Enhanced LangChain Agent Factory")
        print("=" * 60)
        print("\nUsage: python langchain_agent_factory_enhanced.py <BA_enhanced.json>")
        print("\nEnhancements:")
        print("  ✅ Stricter prompt templates for consistent output")
        print("  ✅ Tool validation before execution")
        print("  ✅ Robust Claude Code output parsing")
        print("  ✅ Better error messages for self-correction")
        print("  ✅ Retry logic with exponential backoff")
        print("  ✅ Comprehensive logging")
        print("\nMake sure:")
        print("  ✓ LM Studio is running with Qwen model loaded")
        print("  ✓ Claude Code is installed and configured")
        print("  ✓ MCP servers are connected in Claude")
        print("=" * 60)
        sys.exit(1)
    
    ba_enhanced_path = sys.argv[1]
    
    print(f"\n🏭 MetaFlow Enhanced Agent Factory")
    print("=" * 60)
    print(f"📄 Input: {ba_enhanced_path}")
    print(f"🤖 LLM: Qwen 2.5 14B (local via LM Studio)")
    print(f"🔧 Tools: MCP servers via Claude Code")
    print(f"🛡️  Mode: Enhanced (strict, validated, robust)")
    print("=" * 60)
    
    # Initialize enhanced factory
    factory = LangChainAgentFactory()
    
    # Create all agents
    print("\n⚙️  Creating enhanced agents...")
    agents = factory.create_all_agents(ba_enhanced_path)
    
    print(f"\n✅ Enhanced Agent Factory Complete!")
    print(f"   Created {len(agents)} production-ready agents")
    print(f"   Each agent features:")
    print(f"     • Strict output format enforcement")
    print(f"     • Tool name validation")
    print(f"     • Robust error handling")
    print(f"     • Automatic retry logic")
    print(f"     • Clear success/failure detection")
    
    print(f"\n📊 Agent Summary:")
    for agent_id, agent in agents.items():
        meta = agent.metadata
        print(f"   {meta['position']}. {meta['agent_name']}")
        print(f"      Tools: {', '.join(meta['tool_names'])}")
        print(f"      Max iterations: 10")
        print(f"      Timeout: 300s")
    
    print(f"\n🎯 Agents are ready for workflow execution!")
    print(f"   Next: Use Enhanced LangGraph Workflow Builder")


if __name__ == "__main__":
    main()