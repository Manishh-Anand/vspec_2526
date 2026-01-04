#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
One-Shot Claude Execution Layer
Delegates the entire workflow execution to Claude Code CLI in a single pass.
Preserves the planning (Local LLM) and mapping (tool_mapper) phases.

Changes:
- NO LangGraph execution
- NO Python-side MCP calls
- NO permission bypass attempts
- Uses `claude --print` via stdin for robust execution
"""

import os
import json
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ClaudeExecutor")

class ClaudeOneShotExecutor:
    def __init__(self, ba_enhanced_path: str):
        self.ba_enhanced_path = Path(ba_enhanced_path)
        self.workflow_data = self._load_workflow_data()
        self.workflow_id = self.workflow_data['workflow_metadata'].get('workflow_id', 'unknown_workflow')
        self.user_prompt = self.workflow_data['workflow_metadata'].get('user_prompt', '')
        
        # Output file path
        self.output_file = self.ba_enhanced_path.parent / "workflow_result_claude_code.json"

    def _load_workflow_data(self) -> Dict[str, Any]:
        """Load and validate BA_enhanced.json"""
        if not self.ba_enhanced_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.ba_enhanced_path}")
        
        try:
            with open(self.ba_enhanced_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {self.ba_enhanced_path}: {e}")

    def _extract_valid_tools(self) -> List[str]:
        """
        Extract fully qualified MCP tool names from agents.
        Only keeps tools that look like valid MCP tools (containing 'mcp' or underscores).
        Deduplicates the list.
        """
        valid_tools = set()
        
        for agent in self.workflow_data.get('agents', []):
            for tool in agent.get('tools', []):
                tool_name = tool.get('name', '')
                
                # Filter logic:
                # 1. Must check if mapped (mapping_status is helpful, but name is source of truth)
                # 2. Ignore generic placeholders (if any slipped through)
                # 3. Prefer fully qualified names (contain 'mcp' usually)
                
                # Check mapping status if available (added by tool_mapper.py)
                status = tool.get('mapping_status', '')
                
                if status == 'unmapped' or status == 'placeholder':
                    logger.warning(f"Skipping unmapped tool: {tool_name}")
                    continue

                if not tool_name or tool_name == "general_tool":
                    continue

                valid_tools.add(tool_name)
        
        return sorted(list(valid_tools))

    def _construct_prompt(self, tools: List[str]) -> str:
        """Construct the mega-prompt for Claude Code"""
        
        tools_list_str = "\n".join([f"- {tool}" for tool in tools]) if tools else "No specific MCP tools mapped."
        
        prompt = f"""
SYSTEM CONTEXT:
You are Claude Code with MCP enabled.
You have full permission to use the listed MCP tools.
You must execute real tools, not simulate results.

STRICT RULES:
- Do NOT ask follow-up questions
- Do NOT explain reasoning
- Do NOT show tool traces
- Do NOT simulate outputs
- Execute end-to-end in one pass

AVAILABLE MCP TOOLS:
{tools_list_str}

TASK:
{self.user_prompt}

SUCCESS CRITERIA:
- Perform all required real-world actions
- Use MCP tools where applicable
- Gracefully skip tools that are irrelevant or fail
- If a tool fails, continue with remaining steps

FINAL OUTPUT FORMAT:
Return a concise execution summary including:
- Tools used
- URLs or identifiers of created artifacts
- Any partial failures
"""
        return prompt.strip()

    def execute(self):
        """Execute the one-shot workflow via Claude CLI"""
        logger.info(f"Starting One-Shot Execution for Workflow: {self.workflow_id}")
        
        # 1. Prepare Tools
        valid_tools = self._extract_valid_tools()
        logger.info(f"Identified {len(valid_tools)} valid MCP tools: {valid_tools}")
        
        if not valid_tools:
            logger.warning("No valid MCP tools found! Execution may basically be a text generation.")

        # 2. Construct Prompt
        prompt = self._construct_prompt(valid_tools)
        logger.info("Prioritizing Claude Code execution prompt...")
        # logger.debug(f"Prompt content:\n{prompt}")

        # 3. Invoke Claude Code
        start_time = datetime.now()
        success = False
        raw_output = ""
        error_msg = None

        try:
            logger.info("Invoking `claude --print` via subprocess...")
            
            # Using input=prompt ensures we don't hit command line length limits
            # capture_output=True captures stdout/stderr
            # TEXT=True handles encoding
            process = subprocess.run(
                ["claude.cmd", "--print"],
                input=prompt,
                text=True,
                capture_output=True,
                encoding='utf-8',
                cwd=os.path.expanduser("~"),
                check=False  # We want to handle errors manually
            )
            
            raw_output = process.stdout
            stderr_output = process.stderr
            
            if process.returncode == 0:
                logger.info("Claude execution completed successfully (exit code 0).")
                success = True
            else:
                logger.error(f"Claude execution failed with exit code {process.returncode}")
                logger.error(f"STDERR: {stderr_output}")
                error_msg = f"Exit Code {process.returncode}: {stderr_output}"
                # Still save raw output as it might contain partial work
                if not raw_output and stderr_output: 
                    raw_output = stderr_output

        except FileNotFoundError:
            logger.error("`claude` executable not found in PATH. Is Claude Code installed?")
            error_msg = "`claude` executable not found."
        except Exception as e:
            logger.error(f"Unexpected error during subprocess call: {e}")
            error_msg = str(e)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # 4. Save Result
        self._save_result(success, raw_output, error_msg, duration)

    def _save_result(self, success: bool, raw_output: str, error_msg: str, duration: float):
        """Save the execution result to disk"""
        
        result_data = {
            "success": success,
            "executor": "claude_code_cli",
            "workflow_id": self.workflow_id,
            "executed_at": datetime.now().isoformat(),
            "duration_seconds": duration,
            "error": error_msg,
            "summary": "Check raw_output for execution details.",
            "raw_output": raw_output
        }

        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved execution result to: {self.output_file}")
            
            if success:
                print(f"\n[SUCCESS] One-Shot Execution Complete via Claude Code.")
                print(f"Result saved to: {self.output_file}")
            else:
                print(f"\n[FAILURE] One-Shot Execution Failed.")
                print(f"Error: {error_msg}")
                print(f"See details in: {self.output_file}")

        except Exception as e:
            logger.error(f"Failed to save result file: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python claude_code_executor.py <BA_enhanced.json>")
        sys.exit(1)

    input_file = sys.argv[1]
    
    try:
        executor = ClaudeOneShotExecutor(input_file)
        executor.execute()
    except Exception as e:
        logger.critical(f"Critical execution error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
