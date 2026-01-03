#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MetaFlow Agent Factory - MINIMAL Implementation
Includes: Token Sentinel (symbolic), Pruning Logic (basic), Auto QC (validation only)
Version: A - For thesis demonstration (90% thesis, 10% function)
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

# ============================================================================
# TOKEN SENTINEL CONFIGURATION
# ============================================================================
TOKEN_SENTINEL_CONFIG = {
    "enabled": True,
    "max_tokens_per_iteration": 700,
    "max_tokens_per_agent": 7000,
    "max_tokens_per_workflow": 50000,
    "enforcement_mode": "warn"  # "warn" = log only, "strict" = actually stop
}

class MCPToolInput(BaseModel):
    """Schema for MCP tool input with strict validation"""
    tool_name: str = Field(description="The EXACT name of the MCP tool to execute")
    parameters: Dict[str, Any] = Field(description="Parameters to pass to the tool as a JSON dictionary", default_factory=dict)

class ClaudeMCPTool(BaseTool):
    """Enhanced Universal MCP Tool Wrapper for Claude Code"""

    name: str = "mcp_tool_executor"
    description: str = "Execute MCP tools via Claude Code"
    args_schema: type[BaseModel] = MCPToolInput
    claude_cwd: Path = Field(default_factory=lambda: Path(r"C:\Users\manis"))
    timeout: int = Field(default=300)
    max_retries: int = Field(default=2)
    available_tools: List[str] = Field(default_factory=list)

    def _run(self, tool_name: str = None, parameters: Dict[str, Any] = None, **kwargs) -> str:
        """Execute MCP tool with validation and error handling"""
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
            logger.info(f"[TOOL] Executing MCP tool: {tool_name}")

            # Validate tool name
            if self.available_tools and tool_name not in self.available_tools:
                return f"ERROR: Tool '{tool_name}' is not available. Available tools: {', '.join(self.available_tools)}"

            # Execute with retry logic
            for attempt in range(self.max_retries + 1):
                try:
                    prompt = self._build_claude_prompt(tool_name, parameters)
                    raw_output = self._execute_claude_command(prompt)
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
        if tool_name.startswith("mcp__"):
            parts = tool_name.split("__")
            if len(parts) >= 3:
                tool_name = parts[2]
            elif len(parts) == 2:
                tool_name = parts[1]

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
    """Custom LLM client for LM Studio using requests"""
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
            return type('AIMessage', (object,), {'content': content})()
        except Exception as e:
            raise Exception(f"LM Studio call failed: {e}")

# ============================================================================
# TOKEN SENTINEL - MINIMAL VERSION (Warns but doesn't enforce)
# ============================================================================

class TokenSentinel:
    """
    MINIMAL Token Sentinel - Monitors token usage but doesn't strictly enforce
    For thesis demonstration - shows concept without breaking workflows
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or TOKEN_SENTINEL_CONFIG
        self.enabled = self.config.get("enabled", True)
        self.max_per_iteration = self.config.get("max_tokens_per_iteration", 700)
        self.max_per_agent = self.config.get("max_tokens_per_agent", 7000)
        self.enforcement_mode = self.config.get("enforcement_mode", "warn")

        self.total_tokens = 0
        self.iteration_tokens = []

        if self.enabled:
            logger.info(f"[SENTINEL] Token Sentinel initialized (mode: {self.enforcement_mode})")

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation: ~4 characters per token"""
        return len(text) // 4

    def check_iteration(self, prompt: str, response: str, iteration: int) -> Tuple[bool, str]:
        """
        Check token usage for single iteration
        MINIMAL: Just logs warnings, doesn't actually stop
        Returns: (continue: bool, message: str)
        """
        if not self.enabled:
            return True, ""

        iteration_tokens = self.estimate_tokens(prompt) + self.estimate_tokens(response)
        self.total_tokens += iteration_tokens
        self.iteration_tokens.append(iteration_tokens)

        # Log if threshold exceeded
        if iteration_tokens > self.max_per_iteration:
            msg = f"[WARNING] Iteration {iteration}: {iteration_tokens} tokens (threshold: {self.max_per_iteration})"
            logger.warning(msg)

            # In minimal mode, we continue anyway unless mode is "strict"
            if self.enforcement_mode == "strict":
                return False, f"Token limit exceeded: {iteration_tokens} > {self.max_per_iteration}"
            else:
                return True, msg  # Warn but continue

        return True, ""

    def check_agent_total(self, agent_name: str) -> Tuple[bool, str]:
        """
        Check total token usage for agent
        MINIMAL: Just logs, doesn't stop
        Returns: (continue: bool, message: str)
        """
        if not self.enabled:
            return True, ""

        if self.total_tokens > self.max_per_agent:
            msg = f"[WARNING] Agent {agent_name}: {self.total_tokens} total tokens (threshold: {self.max_per_agent})"
            logger.warning(msg)

            if self.enforcement_mode == "strict":
                return False, f"Agent token limit exceeded: {self.total_tokens} > {self.max_per_agent}"
            else:
                return True, msg

        return True, ""

    def get_stats(self) -> Dict[str, Any]:
        """Get token usage statistics"""
        return {
            "total_tokens": self.total_tokens,
            "iterations": len(self.iteration_tokens),
            "avg_per_iteration": self.total_tokens / len(self.iteration_tokens) if self.iteration_tokens else 0,
            "max_iteration": max(self.iteration_tokens) if self.iteration_tokens else 0,
            "threshold_violations": sum(1 for t in self.iteration_tokens if t > self.max_per_iteration)
        }

# ============================================================================
# SIMPLE AGENT EXECUTOR - With Token Sentinel Integration
# ============================================================================

class SimpleAgentExecutor:
    """
    Custom Agent Executor with Token Sentinel
    MINIMAL version - tracks tokens, logs warnings
    """
    def __init__(self, agent_name, prompt_template, tools, llm, metadata=None):
        self.agent_name = agent_name
        self.prompt_template = prompt_template
        self.tools = {t.name: t for t in tools}
        self.llm = llm
        self.metadata = metadata or {'agent_name': agent_name}
        self.max_iterations = 10

        # Add Token Sentinel
        self.token_sentinel = TokenSentinel()

    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        user_input = inputs.get("input", "")
        chat_history = inputs.get("chat_history", "")

        prompt = self.prompt_template.replace("{{input}}", user_input)
        prompt = prompt.replace("{{chat_history}}", str(chat_history))

        scratchpad = ""
        intermediate_steps = []

        logger.info(f"[AGENT] {self.agent_name} starting ReAct loop")

        for i in range(self.max_iterations):
            current_prompt = prompt.replace("{{agent_scratchpad}}", scratchpad)

            try:
                response = self.llm.invoke(current_prompt)
                response_text = response.content
                logger.info(f"  [THOUGHT] {response_text[:100]}...")

                # TOKEN SENTINEL CHECK
                can_continue, sentinel_msg = self.token_sentinel.check_iteration(
                    current_prompt, response_text, i
                )
                if sentinel_msg:
                    logger.info(f"  [SENTINEL] {sentinel_msg}")

                # Stop only if strict mode and limit exceeded
                if not can_continue:
                    stats = self.token_sentinel.get_stats()
                    return {
                        "output": f"Stopped by Token Sentinel. Stats: {stats}",
                        "intermediate_steps": intermediate_steps,
                        "token_stats": stats
                    }

            except Exception as e:
                return {"output": f"Error calling LLM: {e}", "intermediate_steps": intermediate_steps}

            # Check for Final Answer
            if "Final Answer:" in response_text:
                final_answer = response_text.split("Final Answer:")[-1].strip()
                logger.info(f"  [SUCCESS] Final Answer found")
                stats = self.token_sentinel.get_stats()
                logger.info(f"  [STATS] Token usage: {stats}")
                return {
                    "output": final_answer,
                    "intermediate_steps": intermediate_steps,
                    "token_stats": stats
                }

            # Check for Action
            action_match = re.search(r"Action:\s*(.+)", response_text)
            action_input_match = re.search(r"Action Input:\s*(.+)", response_text, re.DOTALL)

            if action_match and action_input_match:
                action = action_match.group(1).strip()
                action_input_str = action_input_match.group(1).strip()

                last_brace = action_input_str.rfind('}')
                if last_brace != -1:
                    action_input_str = action_input_str[:last_brace+1]

                logger.info(f"  [ACTION] {action}")

                observation = ""
                if action == "mcp_tool_executor":
                    try:
                        tool_call = json.loads(action_input_str)
                        tool_name = tool_call.get("tool_name")
                        parameters = tool_call.get("parameters", {})

                        mcp_tool = list(self.tools.values())[0]
                        observation = mcp_tool._run(tool_name=tool_name, parameters=parameters)

                    except json.JSONDecodeError:
                        observation = "Error: Action Input must be valid JSON"
                    except Exception as e:
                        observation = f"Error executing tool: {e}"
                else:
                    observation = f"Error: Unknown action '{action}'. Only 'mcp_tool_executor' is allowed."

                logger.info(f"  [OBSERVATION] {observation[:100]}...")

                step_log = f"\n{response_text}\nObservation: {observation}\n"
                scratchpad += step_log
                intermediate_steps.append((action, observation))

            else:
                scratchpad += f"\n{response_text}\n"

        # Check agent total before returning
        can_continue, sentinel_msg = self.token_sentinel.check_agent_total(self.agent_name)
        if sentinel_msg:
            logger.info(f"  [SENTINEL] {sentinel_msg}")

        stats = self.token_sentinel.get_stats()
        return {
            "output": "Agent stopped due to max iterations.",
            "intermediate_steps": intermediate_steps,
            "token_stats": stats
        }

# ============================================================================
# PRUNING LOGIC - MINIMAL VERSION (Detects but doesn't modify much)
# ============================================================================

class PruningAgent:
    """
    MINIMAL Pruning Agent - Detects redundancies and logs them
    Rule-based, simple checks
    For thesis: Shows concept without complex modifications
    """
    def __init__(self):
        self.pruned_count = 0
        self.optimization_log = []

    def prune_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply simple pruning rules to workflow
        MINIMAL: Detects issues and logs them, makes minimal changes
        Returns: pruned workflow data
        """
        logger.info("[PRUNING] Starting Pruning Logic...")

        agents = workflow_data.get('agents', [])
        original_count = len(agents)

        # Rule 1: Remove exact duplicates
        agents = self._remove_duplicates(agents)

        # Rule 2: Remove pass-through agents (no tools)
        agents = self._remove_passthrough(agents)

        # Rule 3: Detect similar agents (just log, don't merge in minimal version)
        self._detect_similar(agents)

        workflow_data['agents'] = agents
        self.pruned_count = original_count - len(agents)

        logger.info(f"[PRUNING] Complete: {original_count} -> {len(agents)} ({self.pruned_count} pruned)")
        for log in self.optimization_log:
            logger.info(f"  [OPTIMIZATION] {log}")

        return workflow_data

    def _remove_duplicates(self, agents: List[Dict]) -> List[Dict]:
        """Remove exact duplicates"""
        seen = set()
        unique = []

        for agent in agents:
            sig = (agent['agent_name'], tuple(sorted([t['name'] for t in agent.get('tools', [])])))

            if sig not in seen:
                seen.add(sig)
                unique.append(agent)
            else:
                self.optimization_log.append(f"Removed duplicate: {agent['agent_name']}")

        return unique

    def _remove_passthrough(self, agents: List[Dict]) -> List[Dict]:
        """Remove agents with no tools"""
        filtered = []

        for agent in agents:
            if len(agent.get('tools', [])) == 0:
                self.optimization_log.append(f"Removed pass-through: {agent['agent_name']}")
            else:
                filtered.append(agent)

        return filtered

    def _detect_similar(self, agents: List[Dict]):
        """
        Detect agents with high tool overlap
        MINIMAL: Just log, don't actually merge
        """
        for i, agent1 in enumerate(agents):
            for j, agent2 in enumerate(agents[i+1:], i+1):
                tools1 = set([t['name'] for t in agent1.get('tools', [])])
                tools2 = set([t['name'] for t in agent2.get('tools', [])])

                if tools1 and tools2:
                    overlap = len(tools1 & tools2) / min(len(tools1), len(tools2))
                    if overlap > 0.7:
                        self.optimization_log.append(
                            f"High overlap ({overlap:.0%}) between {agent1['agent_name']} and {agent2['agent_name']} (could merge)"
                        )

# ============================================================================
# AUTO QC - MINIMAL VERSION (Validation only, no auto-fix)
# ============================================================================

class AutoQC:
    """
    MINIMAL Auto QC - Basic validation, reports issues
    For thesis: Shows quality checks without complex auto-correction
    """
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.validation_score = 100.0

    def validate_workflow(self, workflow_data: Dict[str, Any], agents: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run QC checks on workflow and created agents
        MINIMAL: Validates and reports, doesn't auto-fix
        Returns: validation report
        """
        logger.info("[QC] Starting Auto QC...")

        self._check_workflow_structure(workflow_data)
        self._check_agents_created(workflow_data, agents)
        self._check_tool_availability(workflow_data)
        self._check_dependencies(workflow_data)

        # Calculate score
        total_checks = 4
        failed_checks = len(self.issues)
        self.validation_score = ((total_checks - failed_checks) / total_checks) * 100

        report = {
            "status": "PASS" if len(self.issues) == 0 else "FAIL",
            "score": self.validation_score,
            "issues": self.issues,
            "warnings": self.warnings,
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"[QC] Complete: {report['status']} (Score: {self.validation_score:.1f}%)")
        for issue in self.issues:
            logger.error(f"  [ISSUE] {issue}")
        for warning in self.warnings:
            logger.warning(f"  [WARNING] {warning}")

        return report

    def _check_workflow_structure(self, workflow_data: Dict[str, Any]):
        """Check basic workflow structure"""
        required_keys = ['workflow_metadata', 'agents', 'orchestration']
        for key in required_keys:
            if key not in workflow_data:
                self.issues.append(f"Missing required key: {key}")

    def _check_agents_created(self, workflow_data: Dict[str, Any], agents: Dict[str, Any]):
        """Check all agents were created successfully"""
        expected_ids = [a['agent_id'] for a in workflow_data.get('agents', [])]
        created_ids = list(agents.keys())

        for agent_id in expected_ids:
            if agent_id not in created_ids:
                self.issues.append(f"Agent not created: {agent_id}")

    def _check_tool_availability(self, workflow_data: Dict[str, Any]):
        """Check tools are defined for each agent"""
        for agent in workflow_data.get('agents', []):
            tools = agent.get('tools', [])
            if len(tools) == 0:
                self.warnings.append(f"{agent['agent_name']} has no tools")

    def _check_dependencies(self, workflow_data: Dict[str, Any]):
        """Check for missing/circular dependencies"""
        agent_ids = set([a['agent_id'] for a in workflow_data.get('agents', [])])

        for agent in workflow_data.get('agents', []):
            deps = agent.get('interface', {}).get('dependencies', [])
            for dep in deps:
                if dep not in agent_ids:
                    self.warnings.append(f"{agent['agent_name']} depends on unknown agent: {dep}")

# ============================================================================
# ENHANCED FACTORY - With Pruning + QC Integration
# ============================================================================

class LangChainAgentFactory:
    """
    Enhanced Factory with Pruning Logic and Auto QC
    MINIMAL version - demonstrates concepts for thesis
    """

    def __init__(
        self,
        lm_studio_url: str = "http://localhost:1234/v1",
        lm_studio_model: str = "claude-3.7-sonnet-reasoning-gemma3-12b",
        claude_cwd: Path = None,
        enable_pruning: bool = True,
        enable_qc: bool = True
    ):
        self.lm_studio_url = lm_studio_url
        self.lm_studio_model = lm_studio_model
        self.claude_cwd = claude_cwd or Path(r"C:\Users\manis")

        self.enable_pruning = enable_pruning
        self.enable_qc = enable_qc

        self.llm = LMStudioLLM(
            base_url=self.lm_studio_url,
            model=self.lm_studio_model,
            temperature=0.3
        )

        # Initialize components
        self.pruning_agent = PruningAgent() if enable_pruning else None
        self.auto_qc = AutoQC() if enable_qc else None

        logger.info(f"[FACTORY] Enhanced Agent Factory initialized (Pruning: {enable_pruning}, QC: {enable_qc})")

    def create_agent_from_config(self, agent_config: Dict[str, Any]) -> SimpleAgentExecutor:
        """Create single agent from configuration"""
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
        """Build prompt template for agent"""
        agent_name = agent_config['agent_name']
        role = agent_config['identity']['role']
        description = agent_config['identity']['description']

        tool_list = []
        for tool in agent_config['tools']:
            tool_desc = f"  * {tool['name']}: {tool.get('description', 'MCP tool')}"
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
Previous conversation: {{{{chat_history}}}}
Current task: {{{{input}}}}

{{{{agent_scratchpad}}}}"""

    def create_all_agents(self, ba_enhanced_path: str) -> Tuple[Dict[str, SimpleAgentExecutor], Dict[str, Any]]:
        """
        Create all agents with Pruning and QC
        Returns: (agents dict, metadata dict with pruning/QC reports)
        """
        # Load workflow
        with open(ba_enhanced_path, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)

        metadata = {}

        # STEP 1: PRUNING
        if self.enable_pruning and self.pruning_agent:
            workflow_data = self.pruning_agent.prune_workflow(workflow_data)
            metadata['pruning'] = {
                "pruned_count": self.pruning_agent.pruned_count,
                "optimizations": self.pruning_agent.optimization_log
            }

            # Save pruned version
            pruned_path = ba_enhanced_path.replace('.json', '_pruned.json')
            with open(pruned_path, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=2)
            logger.info(f"[PRUNING] Saved pruned workflow to: {pruned_path}")

        # STEP 2: CREATE AGENTS
        agents = {}
        for agent_config in workflow_data['agents']:
            try:
                agent = self.create_agent_from_config(agent_config)
                agents[agent_config['agent_id']] = agent
            except Exception as e:
                logger.error(f"[FACTORY] Failed to create agent {agent_config['agent_id']}: {e}")
                raise

        # STEP 3: AUTO QC
        if self.enable_qc and self.auto_qc:
            qc_report = self.auto_qc.validate_workflow(workflow_data, agents)
            metadata['qc'] = qc_report

            # Save QC report
            qc_path = ba_enhanced_path.replace('.json', '_qc_report.json')
            with open(qc_path, 'w', encoding='utf-8') as f:
                json.dump(qc_report, f, indent=2)
            logger.info(f"[QC] Saved QC report to: {qc_path}")

        return agents, metadata

# ============================================================================
# MAIN EXECUTION (if run directly)
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python langchain_agentfactory_minimal.py <BA_enhanced.json>")
        sys.exit(1)

    ba_enhanced_path = sys.argv[1]

    print("\n" + "="*70)
    print("MetaFlow Agent Factory - MINIMAL Version")
    print("="*70 + "\n")

    factory = LangChainAgentFactory(
        enable_pruning=True,
        enable_qc=True
    )

    agents, metadata = factory.create_all_agents(ba_enhanced_path)

    print(f"\nCreated {len(agents)} agents")
    if 'pruning' in metadata:
        print(f"Pruned: {metadata['pruning']['pruned_count']} agents")
    if 'qc' in metadata:
        print(f"QC Status: {metadata['qc']['status']} (Score: {metadata['qc']['score']}%)")

    print("\nDone!\n")
