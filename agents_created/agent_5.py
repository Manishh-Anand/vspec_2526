#!/usr/bin/env python3
"""
Agent Name: Progress Monitor
Agent ID: agent_5
Generated using the V-Spec Method B+ Architecture
Updated for existing MCP server infrastructure
"""

import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path

# Ensure LangChain components are available
try:
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain.prompts import PromptTemplate
    from langchain.memory import ConversationBufferMemory
    from langchain.tools import Tool
    from langchain_openai import ChatOpenAI
except ImportError:
    raise ImportError("Please install langchain-community and langchain to run this agent.")

# MCP SDK imports for proper server communication
try:
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client, StdioServerParameters
    from mcp.client.streamable_http import streamablehttp_client
except ImportError:
    print("Warning: MCP SDK not found. Tool execution may fail.")
    print("Please install: pip install mcp[cli]")

# --- Agent-Specific Logger ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("agent_5")

class UniversalAgent:
    """A dynamically generated agent for the V-Spec platform with existing MCP server integration."""
    
    def __init__(self):
        # --- Identity ---
        self.agent_id = "agent_5"
        self.agent_name = "Progress Monitor"
        self.position = 5
        
        # --- Initialize Core Components ---
        self.llm = self._initialize_llm()
        self.tools = self._initialize_tools()
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.agent_executor = self._create_agent_executor()
        
        logger.info(f"Initialized Agent: {self.agent_name} ({self.agent_id})")
    
    def _initialize_llm(self):
        """Initializes the LLM using the configuration from the MCP."""
        return ChatOpenAI(
            model="openhermes-2.5-mistral-7b",
            base_url="http://127.0.0.1:1234/v1",
            api_key="lm-studio",
            temperature=0.3,
            max_tokens=1500,
            timeout=30,
            max_retries=2
        )
    
    def _initialize_tools(self) -> List[Tool]:
        """Initializes all matched MCP tools for this agent."""
        tools = []
        # These JSON strings are embedded during generation
        matched_tools_data = """[{"name": "file_reader", "server": "finance_mcp_server", "score": 1.0, "confidence": 1.0}, {"name": "bank_statement_parser", "server": "finance_mcp_server", "score": 1.0, "confidence": 1.0}, {"name": "subscription_detector", "server": "finance_mcp_server", "score": 1.0, "confidence": 1.0}, {"name": "budget_planner_tool", "server": "finance_mcp_server", "score": 0.85, "confidence": 0.9}, {"name": "financial_advice_generator", "server": "finance_mcp_server", "score": 0.95, "confidence": 0.8}, {"name": "spending_pattern_visualizer", "server": "finance_mcp_server", "score": 1.0, "confidence": 1.0}, {"name": "progress_monitor_tool", "server": "finance_mcp_server", "score": 0.85, "confidence": 0.9}]"""
        server_configs_data = """{"finance_mcp_server": {"transport": {"type": "stdio", "command": ["python", "D:\\\\final_yr_project_2526\\\\mcp-module\\\\servers\\\\finance_server.py"]}, "capabilities": {"tools": [{"name": "file_reader", "description": "Tool for file reader operations", "match_score": 1.0, "confidence": 1.0, "reasoning": "The required tool, file_reader, has the same name and purpose as the available tool, file_reader.", "parameters": {}, "auth_required": false}, {"name": "bank_statement_parser", "description": "Tool for bank statement parser operations", "match_score": 1.0, "confidence": 1.0, "reasoning": "The required tool is a bank statement parser which matches the purpose and domain relevance of the available tool 'bank_statement_parser'. The names are identical, further increasing the similarity score.", "parameters": {}, "auth_required": false}, {"name": "subscription_detector", "description": "Tool for detecting recurring subscriptions", "match_score": 1.0, "confidence": 1.0, "reasoning": "The required tool 'subscription_detector' has the same name and purpose as the available tool 'subscription_detector'. Both tools are specifically designed for detecting recurring subscriptions.", "parameters": {}, "auth_required": false}, {"name": "subscription_detector", "description": "Tool for detecting recurring subscriptions", "match_score": 0.85, "confidence": 0.9, "reasoning": "The 'recurring_charge_identifier' tool is closely related to detecting recurring subscriptions. Both tools are used for identifying and analyzing recurring charges or payments. While the 'subscription_detector' is more specific in its purpose, it still shares a strong functional similarity with the required tool.", "parameters": {}, "auth_required": false}, {"name": "budget_planner_tool", "description": "Tool for budget planning and analysis", "match_score": 0.85, "confidence": 0.9, "reasoning": "The budget_planner_tool is the most semantically similar tool to income_expense_tracker as it shares a common purpose of tracking and planning finances.", "parameters": {}, "auth_required": false}, {"name": "budget_planner_tool", "description": "Tool for budget planning and analysis", "match_score": 0.85, "confidence": 0.9, "reasoning": "The required tool 'budget_planner_tool' has a name and purpose that aligns with the available tool 'budget_planner_tool'. Both tools are related to budget planning and analysis, making them functionally similar in the finance domain.", "parameters": {}, "auth_required": false}, {"name": "financial_advice_generator", "description": "Tool for generating financial advice", "match_score": 0.95, "confidence": 0.8, "reasoning": "Functional similarity as both tools are for financial advice generation. Purpose alignment as the required tool is specifically for generating financial advice. Domain relevance as both tools are in the finance domain. Name similarity as the names of both tools contain 'financial_advice'.", "parameters": {}, "auth_required": false}, {"name": "budget_planner_tool", "description": "Tool for budget planning and analysis", "match_score": 0.85, "confidence": 0.9, "reasoning": "The budget_planner_tool is the most semantically similar tool to financial_management_tool as it shares a common purpose of managing finances and planning budgets.", "parameters": {}, "auth_required": false}, {"name": "spending_pattern_visualizer", "description": "Tool for visualizing spending patterns", "match_score": 1.0, "confidence": 1.0, "reasoning": "The required tool is for spending pattern visualization, which matches the purpose of the available 'spending_pattern_visualizer' tool. Both tools are domain-relevant and have similar names.", "parameters": {}, "auth_required": false}, {"name": "spending_pattern_visualizer", "description": "Tool for visualizing spending patterns", "match_score": 0.75, "confidence": 0.9, "reasoning": "The 'graph_chart_creator' tool is functionally similar to the 'spending_pattern_visualizer', as both are used for visualization purposes. Additionally, their purpose aligns with creating and analyzing financial charts or patterns. Both tools are relevant in the finance domain and share a similar name structure.", "parameters": {}, "auth_required": false}, {"name": "progress_monitor_tool", "description": "Tool for monitoring financial progress", "match_score": 0.85, "confidence": 0.9, "reasoning": "The required tool is for progress monitor operations and the available tool with a similar purpose is also a progress monitor tool.", "parameters": {}, "auth_required": false}, {"name": "budget_planner_tool", "description": "Tool for budget planning and analysis", "match_score": 0.85, "confidence": 0.9, "reasoning": "The budget_plan_adjuster tool is related to budget planning and analysis, which aligns with the purpose of the budget_planner_tool. Both tools are relevant in the finance domain.", "parameters": {}, "auth_required": false}], "resources": [], "prompts": []}}}"""
        
        try:
            matched_tools = json.loads(matched_tools_data)
            server_configs = json.loads(server_configs_data)
        except json.JSONDecodeError:
            logger.error("Failed to decode embedded tool or server JSON configuration.")
            return []

        for tool_match in matched_tools:
            tool = self._create_mcp_tool(tool_match, server_configs)
            if tool:
                tools.append(tool)
        
        logger.info(f"Initialized {len(tools)} tools for {self.agent_name}.")
        return tools
    
    def _create_mcp_tool(self, tool_match: Dict, server_configs: Dict) -> Optional[Tool]:
        """Creates a LangChain Tool that communicates with existing MCP servers using the SDK."""
        server_name = tool_match.get('server')
        tool_name = tool_match.get('name')
        
        if not server_name or server_name not in server_configs:
            logger.warning(f"Server '{server_name}' not found for tool '{tool_name}'. Skipping tool.")
            return None
        
        server_config = server_configs[server_name]
        
        async def tool_func_async(input_str: str = "") -> dict:
            """Async function that communicates with MCP server using the SDK."""
            transport_config = server_config.get('transport', {})
            
            if transport_config.get('type') == 'stdio':
                command = transport_config.get('command', [])
                if not command:
                    return {"error": "Missing command in stdio transport config."}
                
                # Check if server file exists
                server_path = Path(command[1]) if len(command) > 1 else None
                if not server_path or not server_path.exists():
                    return {
                        "error": f"MCP server not found at {server_path}",
                        "suggestion": "Please ensure your MCP servers are properly set up in mcp-module/src/servers/"
                    }
                
                try:
                    # Use MCP SDK to communicate with the server
                    server_params = StdioServerParameters(
                        command=command[0],  # python
                        args=command[1:]     # [server_path, additional_args]
                    )
                    
                    async with stdio_client(server_params) as (read, write):
                        async with ClientSession(read, write) as session:
                            # Initialize the session
                            await session.initialize()
                            
                            # Call the tool using the MCP SDK
                            try:
                                # Parse input for MCP tool call
                                if isinstance(input_str, str):
                                    try:
                                        params = json.loads(input_str) if input_str.startswith('{') else {"input": input_str}
                                    except json.JSONDecodeError:
                                        params = {"input": input_str}
                                else:
                                    params = input_str
                                
                                result = await session.call_tool(tool_name, params)
                                return {
                                    "status": "success",
                                    "result": result.content if hasattr(result, 'content') else result,
                                    "tool_name": tool_name
                                }
                            except Exception as tool_error:
                                return {
                                    "status": "error", 
                                    "error": f"Tool execution failed: {str(tool_error)}",
                                    "tool_name": tool_name
                                }
                                
                except Exception as e:
                    logger.error(f"MCP communication error for tool '{tool_name}': {e}")
                    return {
                        "status": "error",
                        "error": f"MCP communication failed: {str(e)}",
                        "tool_name": tool_name
                    }
            else:
                return {
                    "status": "error",
                    "error": f"Unsupported transport type: '{transport_config.get('type')}'"
                }
        
        def tool_func_sync(input_str: str = "") -> dict:
            """Synchronous wrapper for the async tool function."""
            try:
                # Create a new event loop for this thread
                import asyncio
                import threading
                
                def run_async():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(tool_func_async(input_str))
                    finally:
                        new_loop.close()
                
                # Run in a separate thread to avoid blocking
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_async)
                    return future.result(timeout=30)  # 30 second timeout
                    
            except Exception as e:
                logger.error(f"Error in sync wrapper for tool '{tool_name}': {e}")
                return {"status": "error", "error": str(e)}

        tool_description = (
            f"This tool, '{tool_name}', is used to {tool_match.get('description', 'perform a specific task')}. "
            f"It communicates with the MCP server '{server_name}' using the official MCP SDK. "
            f"Confidence score: {tool_match.get('confidence', 0)}."
        )

        return Tool(
            name=tool_name,
            func=tool_func_sync,
            description=tool_description
        )
    
    def _create_agent_executor(self) -> AgentExecutor:
        """Creates the agent executor with improved prompting for local LLMs."""
        
        # Custom ReAct prompt optimized for local LLMs
        react_prompt = """You are Progress Monitor, a Monitor progress and adjust budget plan as needed..

You are a meticulous financial analyst responsible for monitoring progress and adjusting budget plans as needed in a financial workflow. Your primary objective is to ensure that the project stays within the allotted budget while maximizing returns. You receive input from agent_4, which contains detailed reports on current spending and expected future expenses.\n\nYou should analyze these reports with an eye for detail, paying particular attention to any unexpected variances or trends in spending. If necessary, adjust the budget plan accordingly to maintain financial stability. Be sure to document your adjustments clearly so that they can be easily understood by other agents in the workflow.\n\nWhen producing your output, focus on providing concise and actionable information for agent_6. Include a summary of your findings regarding current spending and projected costs, as well as any necessary budgetary changes you have made to address these issues. Use clear language and avoid jargon or technical terms that might be difficult for other agents in the workflow to understand.\n\nIn cases where unexpected events may cause significant disruptions to the project's finances, consider implementing contingency plans or exploring alternative funding sources. If such situations arise, clearly outline your decision-making process and provide rationale for any changes made.\n\nRemember, accuracy and efficiency are key in this role. Your work directly impacts the success of the overall project, so ensure that you are diligent in your analysis and thorough in your recommendations.

You have access to the following tools:
{tools}

Use the following format EXACTLY:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

        prompt = PromptTemplate(
            template=react_prompt,
            input_variables=["input", "agent_scratchpad"],
            partial_variables={
                "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools]),
                "tool_names": ", ".join([tool.name for tool in self.tools]),
                "agent_name": self.agent_name,
                "role": "Monitor progress and adjust budget plan as needed.",
                "system_prompt": "You are a meticulous financial analyst responsible for monitoring progress and adjusting budget plans as needed in a financial workflow. Your primary objective is to ensure that the project stays within the allotted budget while maximizing returns. You receive input from agent_4, which contains detailed reports on current spending and expected future expenses.\n\nYou should analyze these reports with an eye for detail, paying particular attention to any unexpected variances or trends in spending. If necessary, adjust the budget plan accordingly to maintain financial stability. Be sure to document your adjustments clearly so that they can be easily understood by other agents in the workflow.\n\nWhen producing your output, focus on providing concise and actionable information for agent_6. Include a summary of your findings regarding current spending and projected costs, as well as any necessary budgetary changes you have made to address these issues. Use clear language and avoid jargon or technical terms that might be difficult for other agents in the workflow to understand.\n\nIn cases where unexpected events may cause significant disruptions to the project's finances, consider implementing contingency plans or exploring alternative funding sources. If such situations arise, clearly outline your decision-making process and provide rationale for any changes made.\n\nRemember, accuracy and efficiency are key in this role. Your work directly impacts the success of the overall project, so ensure that you are diligent in your analysis and thorough in your recommendations."
            }
        )
        
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            max_execution_time=60,
            return_intermediate_steps=True
        )
    
    async def process(self, input_data: Union[str, Dict]) -> Dict[str, Any]:
        """The main entry point for the agent to process data from the coordinator."""
        logger.info(f"Starting process with input: {input_data}")
        try:
            # Ensure input is a string for the agent executor
            input_str = json.dumps(input_data) if isinstance(input_data, dict) else str(input_data)
            
            # Run the agent executor in a separate thread
            result = await asyncio.to_thread(
                self.agent_executor.invoke,
                {"input": input_str}
            )
            
            output = {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "timestamp": datetime.now().isoformat(),
                "result": result.get("output", "No output generated."),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"CRITICAL ERROR during agent execution: {e}", exc_info=True)
            output = {
                "agent_id": self.agent_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "failure"
            }
        
        logger.info(f"Finished process.")
        return output

# This allows the generated agent file to be tested individually
if __name__ == "__main__":
    async def test_agent_individually():
        agent = UniversalAgent()
        test_input = {"message": "Please perform your primary function based on this test input."}
        result = await agent.process(test_input)
        print(json.dumps(result, indent=2))

    asyncio.run(test_agent_individually())
