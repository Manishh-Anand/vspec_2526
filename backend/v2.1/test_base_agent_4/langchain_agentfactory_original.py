#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MetaFlow Agent Factory - Enhanced Implementation
Production-ready version with custom Agent Executor and LLM Client
"""

import json
import subprocess
import asyncio
import logging
import re
import time
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Available LangChain imports
from langchain_core.tools import BaseTool
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
    """
    tool_name: str = Field(
        description="The EXACT name of the MCP tool to execute"
    )
    parameters: Dict[str, Any] = Field(
        description="Parameters to pass to the tool as a JSON dictionary",
        default_factory=dict
    )


class ClaudeMCPTool(BaseTool):
    """
    Enhanced Universal MCP Tool Wrapper for Claude Code
    """
    
    name: str = "mcp_tool_executor"
    description: str = "Execute MCP tools via Claude Code"
    
    args_schema: type[BaseModel] = MCPToolInput
    claude_cwd: Path = Field(default_factory=lambda: Path(r"C:\Users\manis"))
    timeout: int = Field(default=300)
    max_retries: int = Field(default=2)
    available_tools: List[str] = Field(default_factory=list)
    
    def _run(self, tool_name: str = None, parameters: Dict[str, Any] = None, **kwargs) -> str:
        """
        Execute MCP tool with validation and error handling
        """
        # Handle different ways LangChain might call this
        if tool_name is None and 'tool_name' in kwargs:
            tool_name = kwargs['tool_name']
        if parameters is None and 'parameters' in kwargs:
            parameters = kwargs['parameters']
            
        # Handle JSON string passed as tool_name (common LLM mistake)
        if tool_name and isinstance(tool_name, str) and tool_name.strip().startswith('{'):
            try:
                parsed = json.loads(tool_name)
                if 'tool_name' in parsed:
                    parameters = parsed.get('parameters', {})
                    tool_name = parsed['tool_name']
            except:
                pass

        if tool_name is None:
            return "ERROR: tool_name is required"
        if parameters is None:
            parameters = {}
            
        try:
            logger.info(f"🔧 Executing MCP tool: {tool_name}")
            
            # Validate tool name
            if self.available_tools and tool_name not in self.available_tools:
                return f"ERROR: Tool '{tool_name}' is not available. Available tools: {', '.join(self.available_tools)}"
            
            # Execute with retry logic
            for attempt in range(self.max_retries + 1):
                try:
                    # Build Claude prompt
                    prompt = self._build_claude_prompt(tool_name, parameters)
                    
                    # Execute via subprocess
                    raw_output = self._execute_claude_command(prompt)
                    
                    # Parse output
                    parsed_result = self._parse_claude_output(raw_output, tool_name)
                    
                    return self._format_result_for_agent(parsed_result)
                    
                except Exception as e:
                    if attempt < self.max_retries:
                        time.sleep(2 ** attempt)
                    else:
                        return f"ERROR: Tool execution failed: {str(e)}"
            
        except Exception as e:
            return f"ERROR: Tool execution failed: {str(e)}"
    
    def _build_claude_prompt(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        # Strip MCP prefix
        if tool_name.startswith("mcp__"):
            parts = tool_name.split("__")
            if len(parts) >= 3:
                tool_name = parts[2]
            elif len(parts) == 2:
                tool_name = parts[1]
        
        # Format parameters
        param_str = ", ".join([f"{k}: {v}" for k, v in parameters.items()]) if parameters else "no parameters"
        
        return f"""Execute the MCP tool: {tool_name}
Parameters: {param_str}
Please execute this tool and provide a clear, concise result."""

    def _execute_claude_command(self, prompt: str) -> str:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        input_file = self.claude_cwd / f"mcp_input_{timestamp}.txt"
        
        try:
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            
            cmd = ["powershell.exe", "-NoLogo", "-NoProfile", "-Command", "claude"]
            
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.claude_cwd),
                text=True,
                encoding='utf-8'
            )
            
            with open(input_file, 'r', encoding='utf-8') as f:
                input_data = f.read()
            
            stdout, stderr = proc.communicate(input=input_data, timeout=self.timeout)
            return stdout.strip()
            
        finally:
            if input_file.exists():
                try: input_file.unlink()
                except: pass

    def _parse_claude_output(self, raw_output: str, tool_name: str) -> Dict[str, Any]:
        if not raw_output:
            return {"status": "error", "result": "Empty response", "raw": raw_output}
            
        status = "success"
        lower = raw_output.lower()
        if any(x in lower for x in ["error", "failed", "cannot", "unable"]):
            status = "error"
            
        return {"status": status, "result": raw_output, "tool": tool_name}

    def _format_result_for_agent(self, parsed_result: Dict[str, Any]) -> str:
        return f"Tool '{parsed_result['tool']}' executed.\nResult:\n{parsed_result['result']}"


class LMStudioLLM:
    """
    Custom LLM client for LM Studio using requests
    """
    def __init__(self, base_url, model, temperature=0.3):
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        
    def invoke(self, prompt: str) -> Any:
        url = f"{self.base_url}/chat/completions"
        headers = {"Content-Type": "application/json"}
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": 2000,
            "stream": False
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content']
            # Return object with content attribute to match LangChain interface
            return type('AIMessage', (object,), {'content': content})()
        except Exception as e:
            raise Exception(f"LM Studio call failed: {e}")


class SimpleAgentExecutor:
    """
    Custom Agent Executor to replace broken LangChain AgentExecutor
    Implements a simple ReAct loop
    """
    def __init__(self, agent_name, prompt_template, tools, llm, metadata=None):
        self.agent_name = agent_name
        self.prompt_template = prompt_template
        self.tools = {t.name: t for t in tools}
        self.llm = llm
        self.metadata = metadata or {'agent_name': agent_name}
        self.max_iterations = 10
        
    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        user_input = inputs.get("input", "")
        chat_history = inputs.get("chat_history", "")
        
        # Format prompt
        prompt = self.prompt_template.replace("{{input}}", user_input)
        prompt = prompt.replace("{{chat_history}}", str(chat_history))
        
        scratchpad = ""
        intermediate_steps = []
        
        logger.info(f"🤖 Agent {self.agent_name} starting ReAct loop")
        
        for i in range(self.max_iterations):
            current_prompt = prompt.replace("{{agent_scratchpad}}", scratchpad)
            
            try:
                # Call LLM
                response = self.llm.invoke(current_prompt)
                response_text = response.content
                logger.info(f"   💭 Thought: {response_text[:100]}...")
                
            except Exception as e:
                return {"output": f"Error calling LLM: {e}", "intermediate_steps": intermediate_steps}
            
            # Check for Final Answer
            if "Final Answer:" in response_text:
                final_answer = response_text.split("Final Answer:")[-1].strip()
                logger.info(f"   ✅ Final Answer found")
                return {"output": final_answer, "intermediate_steps": intermediate_steps}
            
            # Check for Action
            action_match = re.search(r"Action:\s*(.+)", response_text)
            action_input_match = re.search(r"Action Input:\s*(.+)", response_text, re.DOTALL)
            
            if action_match and action_input_match:
                action = action_match.group(1).strip()
                action_input_str = action_input_match.group(1).strip()
                
                # Clean up action input (remove trailing text)
                last_brace = action_input_str.rfind('}')
                if last_brace != -1:
                    action_input_str = action_input_str[:last_brace+1]
                
                logger.info(f"   🛠️  Action: {action}")
                
                observation = ""
                if action == "mcp_tool_executor":
                    try:
                        # Parse JSON
                        tool_call = json.loads(action_input_str)
                        tool_name = tool_call.get("tool_name")
                        parameters = tool_call.get("parameters", {})
                        
                        # Execute tool
                        mcp_tool = list(self.tools.values())[0]
                        observation = mcp_tool._run(tool_name=tool_name, parameters=parameters)
                        
                    except json.JSONDecodeError:
                        observation = "Error: Action Input must be valid JSON"
                    except Exception as e:
                        observation = f"Error executing tool: {e}"
                else:
                    observation = f"Error: Unknown action '{action}'. Only 'mcp_tool_executor' is allowed."
                
                logger.info(f"   👀 Observation: {observation[:100]}...")
                
                # Update scratchpad
                step_log = f"\n{response_text}\nObservation: {observation}\n"
                scratchpad += step_log
                intermediate_steps.append((action, observation))
                
            else:
                # No action, append to scratchpad and continue
                scratchpad += f"\n{response_text}\n"
        
        return {"output": "Agent stopped due to max iterations.", "intermediate_steps": intermediate_steps}


class LangChainAgentFactory:
    """
    Enhanced Factory for creating agents
    """
    
    def __init__(
        self, 
        lm_studio_url: str = "http://localhost:1234/v1",
        lm_studio_model: str = "qwen2.5-coder-14b-instruct",
        claude_cwd: Path = None
    ):
        self.lm_studio_url = lm_studio_url
        self.lm_studio_model = lm_studio_model
        self.claude_cwd = claude_cwd or Path(r"C:\Users\manis")
        
        self.llm = LMStudioLLM(
            base_url=self.lm_studio_url,
            model=self.lm_studio_model,
            temperature=0.3
        )
        
        logger.info(f"✅ Enhanced Agent Factory initialized")

    def create_agent_from_config(self, agent_config: Dict[str, Any]) -> SimpleAgentExecutor:
        agent_id = agent_config['agent_id']
        agent_name = agent_config['agent_name']
        
        tool_names = [tool['name'] for tool in agent_config['tools']]
        
        mcp_tool = ClaudeMCPTool(
            claude_cwd=self.claude_cwd,
            available_tools=tool_names
        )
        
        prompt_template = self._build_enhanced_agent_prompt(agent_config)
        
        metadata = {
            'agent_id': agent_id,
            'agent_name': agent_name,
            'position': agent_config['position'],
            'dependencies': agent_config['interface']['dependencies'],
            'outputs_to': agent_config['interface']['outputs_to'],
            'tools': agent_config['tools'],
            'tool_names': tool_names
        }
        
        agent_executor = SimpleAgentExecutor(
            agent_name=agent_name,
            prompt_template=prompt_template,
            tools=[mcp_tool],
            llm=self.llm,
            metadata=metadata
        )
        
        return agent_executor
    
    def _build_enhanced_agent_prompt(self, agent_config: Dict[str, Any]) -> str:
        agent_name = agent_config['agent_name']
        role = agent_config['identity']['role']
        description = agent_config['identity']['description']
        
        tool_list = []
        for tool in agent_config['tools']:
            tool_desc = f"  • {tool['name']}: {tool.get('description', 'MCP tool')}"
            tool_list.append(tool_desc)
        
        tools_text = "\n".join(tool_list)
        tool_names = [tool['name'] for tool in agent_config['tools']]
        
        return f"""You are {agent_name}, a specialized AI agent.

ROLE: {role}
DESCRIPTION: {description}

AVAILABLE TOOLS:
{tools_text}

FORMAT REQUIREMENTS:
You MUST respond using the ReAct format:

Thought: [reasoning]
Action: mcp_tool_executor
Action Input: {{"tool_name": "exact_tool_name", "parameters": {{"param": "value"}}}}
Observation: [result]
...
Final Answer: [response]

RULES:
1. Action Input MUST be valid JSON
2. tool_name MUST be one of: {', '.join(tool_names)}
3. ALWAYS close brackets in JSON

BEGIN:
Previous conversation: {{chat_history}}
Current task: {{input}}

{{agent_scratchpad}}"""

    def create_all_agents(self, ba_enhanced_path: str) -> Dict[str, SimpleAgentExecutor]:
        with open(ba_enhanced_path, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
            
        agents = {}
        for agent_config in workflow_data['agents']:
            try:
                agent = self.create_agent_from_config(agent_config)
                agents[agent_config['agent_id']] = agent
            except Exception as e:
                logger.error(f"❌ Failed to create agent {agent_config['agent_id']}: {e}")
                raise
                
        return agents