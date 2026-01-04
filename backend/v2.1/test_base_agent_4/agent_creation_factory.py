# # # #!/usr/bin/env python3
# # # # -*- coding: utf-8 -*-
# # # """
# # # Agent Creation Factory for MetaFlow Platform
# # # Creates and manages LangChain agents based on BA_enhanced.json specifications
# # # """

# # # import json
# # # import subprocess
# # # import asyncio
# # # import logging
# # # from pathlib import Path
# # # from typing import Dict, List, Any, Optional, Tuple
# # # from abc import ABC, abstractmethod
# # # from datetime import datetime
# # # from dataclasses import dataclass, field
# # # from concurrent.futures import ThreadPoolExecutor
# # # import requests

# # # # Configure logging
# # # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# # # logger = logging.getLogger(__name__)


# # # @dataclass
# # # class AgentMessage:
# # #     """Message structure for inter-agent communication"""
# # #     sender_id: str
# # #     receiver_id: str
# # #     message_type: str  # 'data', 'status', 'error', 'request'
# # #     content: Any
# # #     timestamp: datetime = field(default_factory=datetime.now)
# # #     requires_response: bool = False


# # # @dataclass
# # # class AgentState:
# # #     """Shared state for agent execution"""
# # #     agent_id: str
# # #     status: str  # 'ready', 'running', 'completed', 'failed', 'waiting'
# # #     input_data: Any = None
# # #     output_data: Any = None
# # #     error: Optional[str] = None
# # #     start_time: Optional[datetime] = None
# # #     end_time: Optional[datetime] = None
# # #     dependencies_met: bool = False


# # # class BaseAgent(ABC):
# # #     """
# # #     Universal template for all MetaFlow agents
# # #     Handles common functionality while allowing specific implementations
# # #     """
    
# # #     def __init__(self, agent_config: Dict[str, Any], workflow_context: Dict[str, Any]):
# # #         """
# # #         Initialize base agent with configuration from BA_enhanced.json
        
# # #         Args:
# # #             agent_config: Individual agent configuration from JSON
# # #             workflow_context: Overall workflow metadata and shared resources
# # #         """
# # #         # 1. Agent Identity
# # #         self.agent_id = agent_config['agent_id']
# # #         self.agent_name = agent_config['agent_name']
# # #         self.position = agent_config['position']
# # #         self.identity = agent_config['identity']
        
# # #         # 2. MCP Tool Access
# # #         self.tools = agent_config.get('tools', [])
# # #         self.mcp_executor = MCPToolExecutor(workflow_context.get('claude_cwd', Path(r"C:\Users\manis")))
        
# # #         # 3. Input Processing
# # #         self.data_interface = agent_config['data_interface']
# # #         self.input_types = self.data_interface['input']['types']
# # #         self.output_types = self.data_interface['output']['types']
        
# # #         # 4. Output Formatting
# # #         self.output_delivery = self.data_interface['output']['delivery']
        
# # #         # 5. State Management
# # #         self.state_config = agent_config['state']
# # #         self.local_state = {}
# # #         self.workflow_state = workflow_context.get('shared_state', {})
        
# # #         # 6. Communication Interface
# # #         self.interface_config = agent_config['interface']
# # #         self.dependencies = self.interface_config['dependencies']
# # #         self.outputs_to = self.interface_config['outputs_to']
# # #         self.error_strategy = self.interface_config['error_strategy']
# # #         self.message_queue = asyncio.Queue()
        
# # #         # LLM Configuration
# # #         self.llm_config = agent_config['llm_config']
# # #         self.reasoning_type = self.llm_config['reasoning']  # 'function-calling' or 'ReAct'
        
# # #         # Initialize local LLM connection
# # #         self.local_llm_url = workflow_context.get('llm_url', "http://localhost:1234/v1/chat/completions")
        
# # #         logger.info(f"✅ Initialized {self.agent_name} (ID: {self.agent_id})")
# # #         logger.info(f"   Tools: {[t['name'] for t in self.tools]}")
# # #         logger.info(f"   Dependencies: {self.dependencies}")
    
# # #     @abstractmethod
# # #     async def execute(self, input_data: Any) -> Any:
# # #         """
# # #         Main execution method - must be implemented by each specific agent
        
# # #         Args:
# # #             input_data: Input from previous agent or initial data
            
# # #         Returns:
# # #             Processed output for next agent
# # #         """
# # #         pass
    
# # #     async def run(self, input_data: Any = None) -> AgentState:
# # #         """
# # #         Wrapper method that handles common execution logic
# # #         """
# # #         logger.info(f"🚀 {self.agent_name} starting execution...")
        
# # #         # Initialize state
# # #         state = AgentState(
# # #             agent_id=self.agent_id,
# # #             status='running',
# # #             input_data=input_data,
# # #             start_time=datetime.now()
# # #         )
        
# # #         try:
# # #             # Validate input
# # #             if not self._validate_input(input_data):
# # #                 raise ValueError(f"Invalid input type for {self.agent_name}")
            
# # #             # Execute agent-specific logic
# # #             output = await self.execute(input_data)
            
# # #             # Format output
# # #             formatted_output = self._format_output(output)
            
# # #             # Update state
# # #             state.output_data = formatted_output
# # #             state.status = 'completed'
# # #             state.end_time = datetime.now()
            
# # #             logger.info(f"✅ {self.agent_name} completed successfully")
            
# # #         except Exception as e:
# # #             state.status = 'failed'
# # #             state.error = str(e)
# # #             state.end_time = datetime.now()
            
# # #             logger.error(f"❌ {self.agent_name} failed: {e}")
            
# # #             # Handle error based on strategy
# # #             if self.error_strategy == 'retry':
# # #                 logger.info(f"🔄 Retrying {self.agent_name}...")
# # #                 # Implement retry logic here
            
# # #         return state
    
# # #     def _validate_input(self, input_data: Any) -> bool:
# # #         """Validate input data against expected types"""
# # #         if input_data is None:
# # #             return 'null' in self.input_types or not self.input_types
        
# # #         if isinstance(input_data, dict) and 'json' in self.input_types:
# # #             return True
# # #         if isinstance(input_data, str) and 'text' in self.input_types:
# # #             return True
        
# # #         return False
    
# # #     def _format_output(self, output: Any) -> Any:
# # #         """Format output according to interface requirements"""
# # #         if 'json' in self.output_types and isinstance(output, str):
# # #             try:
# # #                 return json.loads(output)
# # #             except:
# # #                 return {"text": output}
        
# # #         return output
    
# # #     async def call_local_llm(self, prompt: str) -> str:
# # #         """
# # #         Call local LLM (Qwen2.5) for reasoning
# # #         """
# # #         try:
# # #             # Prepare messages based on reasoning type
# # #             if self.reasoning_type == 'function-calling':
# # #                 messages = [
# # #                     {"role": "system", "content": f"You are {self.agent_name}. {self.identity['role']}"},
# # #                     {"role": "user", "content": prompt}
# # #                 ]
# # #             else:  # ReAct
# # #                 messages = [
# # #                     {"role": "system", "content": f"You are {self.agent_name}. {self.identity['role']} Use the ReAct pattern: Thought, Action, Observation, Result."},
# # #                     {"role": "user", "content": prompt}
# # #                 ]
            
# # #             response = requests.post(
# # #                 self.local_llm_url,
# # #                 json={
# # #                     "model": self.llm_config['model'],
# # #                     "messages": messages,
# # #                     "temperature": self.llm_config['params']['temperature'],
# # #                     "max_tokens": self.llm_config['params']['max_tokens']
# # #                 },
# # #                 timeout=60
# # #             )
            
# # #             if response.status_code == 200:
# # #                 return response.json()['choices'][0]['message']['content']
# # #             else:
# # #                 raise Exception(f"LLM call failed: {response.status_code}")
                
# # #         except Exception as e:
# # #             logger.error(f"Failed to call local LLM: {e}")
# # #             raise
    
# # #     async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
# # #         """
# # #         Execute an MCP tool via Claude Code
# # #         """
# # #         # Find the full tool info
# # #         tool_info = next((t for t in self.tools if t['name'] == tool_name), None)
# # #         if not tool_info:
# # #             raise ValueError(f"Tool {tool_name} not found in agent's tool list")
        
# # #         return await self.mcp_executor.execute_tool(tool_info, parameters)
    
# # #     async def send_message(self, receiver_id: str, message_type: str, content: Any):
# # #         """Send message to another agent"""
# # #         message = AgentMessage(
# # #             sender_id=self.agent_id,
# # #             receiver_id=receiver_id,
# # #             message_type=message_type,
# # #             content=content
# # #         )
# # #         # In real implementation, this would use a message broker
# # #         logger.info(f"📧 {self.agent_name} -> {receiver_id}: {message_type}")
        
# # #     def update_shared_state(self, key: str, value: Any):
# # #         """Update shared workflow state"""
# # #         self.workflow_state[key] = value
# # #         logger.info(f"📝 {self.agent_name} updated shared state: {key}")


# # # class MCPToolExecutor:
# # #     """
# # #     Handles execution of MCP tools via Claude Code
# # #     """
    
# # #     def __init__(self, claude_cwd: Path):
# # #         self.claude_cwd = claude_cwd
# # #         self.claude_cmd = [
# # #             "powershell.exe",
# # #             "-NoLogo",
# # #             "-NoProfile",
# # #             "-Command",
# # #             "claude"
# # #         ]
# # #         self.timeout = 300
    
# # #     async def execute_tool(self, tool_info: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
# # #         """
# # #         Execute MCP tool by generating natural language prompt for Claude
        
# # #         Args:
# # #             tool_info: Tool information including name and server
# # #             parameters: Parameters to pass to the tool
            
# # #         Returns:
# # #             Execution result
# # #         """
# # #         tool_name = tool_info['name']
        
# # #         # Create natural language prompt for Claude Code
# # #         param_str = ", ".join([f"{k}='{v}'" for k, v in parameters.items()])
# # #         prompt = f"Use the {tool_name} tool with these parameters: {param_str}"
        
# # #         logger.info(f"🔧 Executing tool: {tool_name}")
# # #         logger.info(f"   Prompt: {prompt}")
        
# # #         try:
# # #             # Execute via subprocess
# # #             result = await asyncio.get_event_loop().run_in_executor(
# # #                 None, 
# # #                 self._execute_claude_command, 
# # #                 prompt
# # #             )
            
# # #             # Parse result
# # #             return self._parse_tool_result(result, tool_name)
            
# # #         except Exception as e:
# # #             logger.error(f"Tool execution failed: {e}")
# # #             return {
# # #                 "success": False,
# # #                 "error": str(e),
# # #                 "tool": tool_name
# # #             }
    
# # #     def _execute_claude_command(self, prompt: str) -> str:
# # #         """Execute Claude command synchronously"""
# # #         # Write prompt to input file
# # #         input_file = self.claude_cwd / "tool_input.txt"
# # #         with open(input_file, 'w', encoding='utf-8') as f:
# # #             f.write(prompt)
        
# # #         # Execute Claude
# # #         proc = subprocess.Popen(
# # #             self.claude_cmd,
# # #             stdin=subprocess.PIPE,
# # #             stdout=subprocess.PIPE,
# # #             stderr=subprocess.PIPE,
# # #             cwd=str(self.claude_cwd),
# # #             text=True,
# # #             encoding='utf-8'
# # #         )
        
# # #         # Feed input
# # #         with open(input_file, 'r', encoding='utf-8') as f:
# # #             input_data = f.read()
        
# # #         stdout, stderr = proc.communicate(input=input_data, timeout=self.timeout)
        
# # #         # Clean up
# # #         if input_file.exists():
# # #             input_file.unlink()
        
# # #         return stdout
    
# # #     def _parse_tool_result(self, raw_output: str, tool_name: str) -> Dict[str, Any]:
# # #         """Parse tool execution result from Claude output"""
# # #         # Basic parsing - can be enhanced based on actual output patterns
# # #         if "error" in raw_output.lower() or "failed" in raw_output.lower():
# # #             return {
# # #                 "success": False,
# # #                 "output": raw_output,
# # #                 "tool": tool_name
# # #             }
        
# # #         return {
# # #             "success": True,
# # #             "output": raw_output,
# # #             "tool": tool_name
# # #         }


# # # class DynamicAgent(BaseAgent):
# # #     """
# # #     Generic agent implementation that can handle any agent type
# # #     Uses the local LLM to determine actions based on role
# # #     """
    
# # #     async def execute(self, input_data: Any) -> Any:
# # #         """
# # #         Dynamic execution based on agent role and available tools
# # #         """
# # #         # Build context for LLM
# # #         context = {
# # #             "role": self.identity['role'],
# # #             "input": input_data,
# # #             "available_tools": [t['name'] for t in self.tools],
# # #             "position": self.position,
# # #             "outputs_to": self.outputs_to
# # #         }
        
# # #         # Create prompt for local LLM
# # #         prompt = self._build_execution_prompt(context)
        
# # #         # Get LLM response
# # #         llm_response = await self.call_local_llm(prompt)
        
# # #         # Parse and execute any tool calls
# # #         result = await self._process_llm_response(llm_response)
        
# # #         return result
    
# # #     def _build_execution_prompt(self, context: Dict[str, Any]) -> str:
# # #         """Build prompt for LLM based on agent context"""
# # #         prompt = f"""
# # # You are {self.agent_name} with the following role:
# # # {context['role']}

# # # Input received: {json.dumps(context['input'], indent=2) if isinstance(context['input'], dict) else context['input']}

# # # Available tools: {', '.join(context['available_tools'])}

# # # Based on your role and the input, determine what actions to take.
# # # If you need to use tools, respond in this format:
# # # TOOL_CALL: tool_name
# # # PARAMETERS: 
# # #   param1: value1
# # #   param2: value2

# # # After any tool calls, provide your final output that will be passed to the next agent.

# # # Remember: You are agent {context['position']} in the workflow. Your output goes to: {context['outputs_to']}
# # # """
# # #         return prompt
    
# # #     async def _process_llm_response(self, response: str) -> Any:
# # #         """Process LLM response and execute any tool calls"""
# # #         lines = response.split('\n')
# # #         final_output = []
        
# # #         i = 0
# # #         while i < len(lines):
# # #             line = lines[i].strip()
            
# # #             # Check for tool call
# # #             if line.startswith("TOOL_CALL:"):
# # #                 tool_name = line.split(":", 1)[1].strip()
# # #                 parameters = {}
                
# # #                 # Parse parameters
# # #                 i += 1
# # #                 if i < len(lines) and lines[i].strip() == "PARAMETERS:":
# # #                     i += 1
# # #                     while i < len(lines) and lines[i].strip() and not lines[i].startswith("TOOL_CALL:"):
# # #                         param_line = lines[i].strip()
# # #                         if ':' in param_line:
# # #                             key, value = param_line.split(':', 1)
# # #                             parameters[key.strip()] = value.strip()
# # #                         i += 1
                
# # #                 # Execute tool
# # #                 result = await self.execute_tool(tool_name, parameters)
# # #                 final_output.append(result)
# # #             else:
# # #                 if line and not line.startswith("PARAMETERS:"):
# # #                     final_output.append(line)
# # #                 i += 1
        
# # #         # Return appropriate format
# # #         if len(final_output) == 1:
# # #             return final_output[0]
# # #         else:
# # #             return '\n'.join(str(item) for item in final_output)


# # # class AgentFactory:
# # #     """
# # #     Factory for creating agents from BA_enhanced.json
# # #     """
    
# # #     def __init__(self, llm_url: str = "http://localhost:1234/v1/chat/completions", output_dir: str = None):
# # #         self.llm_url = llm_url
# # #         self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "created_agents"
# # #         self.workflow_context = {
# # #             'llm_url': llm_url,
# # #             'claude_cwd': Path(r"C:\Users\manis"),
# # #             'shared_state': {}
# # #         }
    
# # #     def create_agent(self, agent_config: Dict[str, Any]) -> BaseAgent:
# # #         """
# # #         Create an agent instance based on configuration
        
# # #         Args:
# # #             agent_config: Agent configuration from BA_enhanced.json
            
# # #         Returns:
# # #             Instantiated agent
# # #         """
# # #         # For now, all agents use the DynamicAgent implementation
# # #         # In future, we could have specialized classes for certain agent types
        
# # #         agent = DynamicAgent(agent_config, self.workflow_context)
# # #         return agent
    
# # #     def create_agent_file(self, agent_config: Dict[str, Any], workflow_id: str) -> Path:
# # #         """
# # #         Create a standalone Python file for an individual agent
        
# # #         Args:
# # #             agent_config: Agent configuration from BA_enhanced.json
# # #             workflow_id: Workflow identifier for organization
            
# # #         Returns:
# # #             Path to created agent file
# # #         """
# # #         # Ensure output directory exists
# # #         agent_dir = self.output_dir / workflow_id
# # #         agent_dir.mkdir(parents=True, exist_ok=True)
        
# # #         # Clean agent name for filename
# # #         agent_name = agent_config['agent_name'].replace('*', '').replace(' ', '_').lower()
# # #         filename = f"{agent_config['agent_id']}_{agent_name}.py"
# # #         filepath = agent_dir / filename
        
# # #         # Generate agent code
# # #         agent_code = self._generate_agent_code(agent_config)
        
# # #         # Write to file
# # #         with open(filepath, 'w', encoding='utf-8') as f:
# # #             f.write(agent_code)
        
# # #         logger.info(f"📄 Created agent file: {filepath}")
# # #         return filepath
    
# # #     def _generate_agent_code(self, agent_config: Dict[str, Any]) -> str:
# # #         """
# # #         Generate standalone Python code for an agent
# # #         """
# # #         agent_name = agent_config['agent_name'].replace('*', '').strip()
# # #         class_name = ''.join(word.capitalize() for word in agent_name.replace('-', ' ').replace('_', ' ').split())
        
# # #         code = f'''#!/usr/bin/env python3
# # # # -*- coding: utf-8 -*-
# # # """
# # # {agent_name} - Auto-generated agent for MetaFlow
# # # Position: {agent_config['position']}
# # # Role: {agent_config['identity']['role']}
# # # """

# # # from pathlib import Path
# # # from typing import Dict, List, Any, Optional
# # # import json
# # # import logging
# # # import asyncio
# # # from datetime import datetime

# # # # Import base agent (this would need to be in Python path)
# # # # from agent_creation_factory import BaseAgent, MCPToolExecutor

# # # logger = logging.getLogger(__name__)


# # # class {class_name}:
# # #     """
# # #     {agent_config['identity']['description']}
# # #     """
    
# # #     def __init__(self):
# # #         # Agent Identity
# # #         self.agent_id = "{agent_config['agent_id']}"
# # #         self.agent_name = "{agent_config['agent_name']}"
# # #         self.position = {agent_config['position']}
        
# # #         # Role Definition
# # #         self.role = """{agent_config['identity']['role']}"""
# # #         self.agent_type = "{agent_config['identity']['agent_type']}"
        
# # #         # Tools Configuration
# # #         self.tools = {json.dumps(agent_config['tools'], indent=8)}
        
# # #         # Data Interface
# # #         self.input_types = {agent_config['data_interface']['input']['types']}
# # #         self.output_types = {agent_config['data_interface']['output']['types']}
# # #         self.output_delivery = "{agent_config['data_interface']['output']['delivery']}"
        
# # #         # LLM Configuration
# # #         self.llm_config = {{
# # #             "provider": "{agent_config['llm_config']['provider']}",
# # #             "model": "{agent_config['llm_config']['model']}",
# # #             "reasoning": "{agent_config['llm_config']['reasoning']}",
# # #             "temperature": {agent_config['llm_config']['params']['temperature']},
# # #             "max_tokens": {agent_config['llm_config']['params']['max_tokens']}
# # #         }}
        
# # #         # Dependencies and Outputs
# # #         self.dependencies = {agent_config['interface']['dependencies']}
# # #         self.outputs_to = {agent_config['interface']['outputs_to']}
# # #         self.error_strategy = "{agent_config['interface']['error_strategy']}"
        
# # #         logger.info(f"✅ Initialized {{self.agent_name}} (ID: {{self.agent_id}})")
    
# # #     async def execute(self, input_data: Any) -> Any:
# # #         """
# # #         Execute the agent's main task
        
# # #         Args:
# # #             input_data: Input from previous agent or initial data
            
# # #         Returns:
# # #             Processed output for next agent
# # #         """
# # #         logger.info(f"🚀 {{self.agent_name}} starting execution...")
        
# # #         try:
# # #             # Agent-specific logic based on role
# # #             result = await self._process_task(input_data)
            
# # #             logger.info(f"✅ {{self.agent_name}} completed successfully")
# # #             return result
            
# # #         except Exception as e:
# # #             logger.error(f"❌ {{self.agent_name}} failed: {{e}}")
# # #             raise
    
# # #     async def _process_task(self, input_data: Any) -> Any:
# # #         """
# # #         Main processing logic for {agent_name}
        
# # #         This method should:
# # #         1. Analyze the input based on the agent's role
# # #         2. Use LLM for reasoning if needed
# # #         3. Execute required tools
# # #         4. Format and return the output
# # #         """
# # #         # TODO: Implement specific logic based on role:
# # #         # {agent_config['identity']['role']}
        
# # #         # For now, return a placeholder
# # #         return {{
# # #             "agent": self.agent_name,
# # #             "status": "processed",
# # #             "input_received": input_data,
# # #             "timestamp": datetime.now().isoformat(),
# # #             "next_agent": self.outputs_to[0] if self.outputs_to else None
# # #         }}
    
# # #     def get_info(self) -> Dict[str, Any]:
# # #         """Get agent information"""
# # #         return {{
# # #             "agent_id": self.agent_id,
# # #             "agent_name": self.agent_name,
# # #             "position": self.position,
# # #             "role": self.role,
# # #             "tools": [tool["name"] for tool in self.tools],
# # #             "dependencies": self.dependencies,
# # #             "outputs_to": self.outputs_to
# # #         }}


# # # # Standalone execution for testing
# # # if __name__ == "__main__":
# # #     async def test_agent():
# # #         agent = {class_name}()
# # #         print(f"Agent Info: {{json.dumps(agent.get_info(), indent=2)}}")
        
# # #         # Test execution with sample input
# # #         test_input = {{"test": "data", "timestamp": datetime.now().isoformat()}}
# # #         result = await agent.execute(test_input)
# # #         print(f"Execution Result: {{json.dumps(result, indent=2, default=str)}}")
    
# # #     asyncio.run(test_agent())
# # # '''
        
# # #         return code
    
# # #     def create_workflow(self, ba_enhanced_path: str) -> 'WorkflowOrchestrator':
# # #         """
# # #         Create complete workflow from BA_enhanced.json
        
# # #         Args:
# # #             ba_enhanced_path: Path to BA_enhanced.json file
            
# # #         Returns:
# # #             WorkflowOrchestrator instance
# # #         """
# # #         # Load configuration
# # #         with open(ba_enhanced_path, 'r', encoding='utf-8') as f:
# # #             workflow_data = json.load(f)
        
# # #         workflow_id = workflow_data['workflow_metadata']['workflow_id']
        
# # #         # Create individual agent files
# # #         logger.info(f"📁 Creating agent files in: {self.output_dir / workflow_id}")
# # #         for agent_config in workflow_data['agents']:
# # #             self.create_agent_file(agent_config, workflow_id)
        
# # #         # Create workflow documentation
# # #         self._create_workflow_docs(workflow_data, workflow_id)
        
# # #         # Create agents for runtime
# # #         agents = {}
# # #         for agent_config in workflow_data['agents']:
# # #             agent = self.create_agent(agent_config)
# # #             agents[agent.agent_id] = agent
        
# # #         # Create orchestrator
# # #         orchestrator = WorkflowOrchestrator(
# # #             agents=agents,
# # #             workflow_metadata=workflow_data['workflow_metadata'],
# # #             orchestration_config=workflow_data['orchestration']
# # #         )
        
# # #         return orchestrator
    
# # #     def _create_workflow_docs(self, workflow_data: Dict, workflow_id: str):
# # #         """Create workflow documentation file"""
# # #         doc_path = self.output_dir / workflow_id / "workflow_documentation.md"
        
# # #         doc_content = f"""# Workflow Documentation: {workflow_id}

# # # ## Overview
# # # - **Domain**: {workflow_data['workflow_metadata']['domain']}
# # # - **Architecture**: {workflow_data['workflow_metadata']['selected_architecture']}
# # # - **Total Agents**: {workflow_data['workflow_metadata']['total_agents']}
# # # - **Estimated Execution Time**: {workflow_data['workflow_metadata']['estimated_execution_time']}

# # # ## Agent Pipeline

# # # """
# # #         for agent in workflow_data['agents']:
# # #             doc_content += f"""### {agent['position']}. {agent['agent_name']}
# # # - **ID**: {agent['agent_id']}
# # # - **Role**: {agent['identity']['role']}
# # # - **Tools**: {', '.join([t['name'] for t in agent['tools']])}
# # # - **Dependencies**: {', '.join(agent['interface']['dependencies']) or 'None'}
# # # - **Outputs To**: {', '.join(agent['interface']['outputs_to']) or 'None'}

# # # """
        
# # #         doc_content += f"""## Orchestration Pattern
# # # - **Type**: {workflow_data['orchestration']['pattern']}
# # # - **Connections**: {len(workflow_data['orchestration']['connections'])} connections

# # # ## Usage
# # # ```python
# # # from agent_creation_factory import AgentFactory

# # # factory = AgentFactory()
# # # workflow = factory.create_workflow("{workflow_id}/BA_enhanced.json")
# # # result = await workflow.execute(initial_input)
# # # ```
# # # """
        
# # #         with open(doc_path, 'w', encoding='utf-8') as f:
# # #             f.write(doc_content)
        
# # #         logger.info(f"📝 Created workflow documentation: {doc_path}")


# # # class WorkflowOrchestrator:
# # #     """
# # #     Manages workflow execution based on selected architecture pattern
# # #     """
    
# # #     def __init__(self, agents: Dict[str, BaseAgent], workflow_metadata: Dict, orchestration_config: Dict):
# # #         self.agents = agents
# # #         self.metadata = workflow_metadata
# # #         self.orchestration = orchestration_config
# # #         self.pattern = orchestration_config['pattern']
# # #         self.connections = orchestration_config['connections']
        
# # #         # State tracking
# # #         self.agent_states = {
# # #             agent_id: AgentState(agent_id=agent_id, status='ready')
# # #             for agent_id in agents.keys()
# # #         }
        
# # #         logger.info(f"📊 Workflow Orchestrator initialized")
# # #         logger.info(f"   Pattern: {self.pattern}")
# # #         logger.info(f"   Total agents: {len(self.agents)}")
    
# # #     async def execute(self, initial_input: Any = None) -> Dict[str, Any]:
# # #         """
# # #         Execute the workflow based on the orchestration pattern
# # #         """
# # #         logger.info(f"🎯 Starting workflow execution: {self.metadata['workflow_id']}")
# # #         logger.info(f"   Architecture: {self.metadata['selected_architecture']}")
        
# # #         start_time = datetime.now()
        
# # #         try:
# # #             if "pipeline" in self.pattern.lower() or "sequential" in self.pattern.lower():
# # #                 result = await self._execute_pipeline(initial_input)
# # #             elif "event" in self.pattern.lower():
# # #                 result = await self._execute_event_driven(initial_input)
# # #             elif "hub" in self.pattern.lower():
# # #                 result = await self._execute_hub_spoke(initial_input)
# # #             elif "hierarchical" in self.pattern.lower():
# # #                 result = await self._execute_hierarchical(initial_input)
# # #             elif "collaborative" in self.pattern.lower():
# # #                 result = await self._execute_collaborative(initial_input)
# # #             else:
# # #                 # Default to pipeline
# # #                 result = await self._execute_pipeline(initial_input)
            
# # #             end_time = datetime.now()
# # #             duration = (end_time - start_time).total_seconds()
            
# # #             logger.info(f"✅ Workflow completed in {duration:.2f} seconds")
            
# # #             return {
# # #                 "success": True,
# # #                 "workflow_id": self.metadata['workflow_id'],
# # #                 "duration": duration,
# # #                 "result": result,
# # #                 "agent_states": self._get_states_summary()
# # #             }
            
# # #         except Exception as e:
# # #             logger.error(f"❌ Workflow failed: {e}")
# # #             return {
# # #                 "success": False,
# # #                 "workflow_id": self.metadata['workflow_id'],
# # #                 "error": str(e),
# # #                 "agent_states": self._get_states_summary()
# # #             }
    
# # #     async def _execute_pipeline(self, initial_input: Any) -> Any:
# # #         """Execute agents in sequential pipeline"""
# # #         current_input = initial_input
        
# # #         # Get agents sorted by position
# # #         sorted_agents = sorted(self.agents.values(), key=lambda a: a.position)
        
# # #         for agent in sorted_agents:
# # #             logger.info(f"🔄 Executing agent {agent.position}: {agent.agent_name}")
            
# # #             # Run agent
# # #             state = await agent.run(current_input)
# # #             self.agent_states[agent.agent_id] = state
            
# # #             if state.status == 'failed':
# # #                 raise Exception(f"Agent {agent.agent_name} failed: {state.error}")
            
# # #             # Pass output to next agent
# # #             current_input = state.output_data
        
# # #         return current_input
    
# # #     async def _execute_event_driven(self, initial_input: Any) -> Any:
# # #         """Execute event-driven architecture"""
# # #         # TODO: Implement event-driven execution
# # #         # For now, fall back to pipeline
# # #         logger.warning("Event-driven execution not yet implemented, using pipeline")
# # #         return await self._execute_pipeline(initial_input)
    
# # #     async def _execute_hub_spoke(self, initial_input: Any) -> Any:
# # #         """Execute hub-and-spoke architecture"""
# # #         # TODO: Implement hub-spoke execution
# # #         # For now, fall back to pipeline
# # #         logger.warning("Hub-spoke execution not yet implemented, using pipeline")
# # #         return await self._execute_pipeline(initial_input)
    
# # #     async def _execute_hierarchical(self, initial_input: Any) -> Any:
# # #         """Execute hierarchical architecture"""
# # #         # TODO: Implement hierarchical execution
# # #         # For now, fall back to pipeline
# # #         logger.warning("Hierarchical execution not yet implemented, using pipeline")
# # #         return await self._execute_pipeline(initial_input)
    
# # #     async def _execute_collaborative(self, initial_input: Any) -> Any:
# # #         """Execute collaborative architecture"""
# # #         # TODO: Implement collaborative execution
# # #         # For now, fall back to pipeline
# # #         logger.warning("Collaborative execution not yet implemented, using pipeline")
# # #         return await self._execute_pipeline(initial_input)
    
# # #     def _get_states_summary(self) -> Dict[str, Dict]:
# # #         """Get summary of all agent states"""
# # #         summary = {}
# # #         for agent_id, state in self.agent_states.items():
# # #             summary[agent_id] = {
# # #                 "status": state.status,
# # #                 "error": state.error,
# # #                 "duration": (state.end_time - state.start_time).total_seconds() if state.end_time and state.start_time else None
# # #             }
# # #         return summary


# # # # Example usage
# # # async def main():
# # #     """Example of how to use the Agent Factory"""
# # #     import sys
    
# # #     if len(sys.argv) < 2:
# # #         print("Usage: python agent_creation_factory.py <path_to_BA_enhanced.json> [initial_input]")
# # #         sys.exit(1)
    
# # #     ba_enhanced_path = sys.argv[1]
    
# # #     # Initialize factory
# # #     factory = AgentFactory()
    
# # #     # Create workflow from BA_enhanced.json
# # #     workflow = factory.create_workflow(ba_enhanced_path)
    
# # #     # Get initial input from command line or use default
# # #     if len(sys.argv) > 2:
# # #         initial_input = {"user_request": sys.argv[2]}
# # #     else:
# # #         initial_input = None
    
# # #     result = await workflow.execute(initial_input)
    
# # #     # Print results
# # #     print(json.dumps(result, indent=2, default=str))


# # # if __name__ == "__main__":
# # #     # Run example
# # #     asyncio.run(main())

# # #!/usr/bin/env python3
# # # -*- coding: utf-8 -*-
# # """
# # Agent Creation Factory for MetaFlow Platform
# # Creates and manages LangChain agents based on BA_enhanced.json specifications
# # """

# # import json
# # import subprocess
# # import asyncio
# # import logging
# # from pathlib import Path
# # from typing import Dict, List, Any, Optional, Tuple
# # from abc import ABC, abstractmethod
# # from datetime import datetime
# # from dataclasses import dataclass, field
# # from concurrent.futures import ThreadPoolExecutor
# # import requests

# # # Configure logging
# # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# # logger = logging.getLogger(__name__)


# # @dataclass
# # class AgentMessage:
# #     """Message structure for inter-agent communication"""
# #     sender_id: str
# #     receiver_id: str
# #     message_type: str  # 'data', 'status', 'error', 'request'
# #     content: Any
# #     timestamp: datetime = field(default_factory=datetime.now)
# #     requires_response: bool = False


# # @dataclass
# # class AgentState:
# #     """Shared state for agent execution"""
# #     agent_id: str
# #     status: str  # 'ready', 'running', 'completed', 'failed', 'waiting'
# #     input_data: Any = None
# #     output_data: Any = None
# #     error: Optional[str] = None
# #     start_time: Optional[datetime] = None
# #     end_time: Optional[datetime] = None
# #     dependencies_met: bool = False


# # class BaseAgent(ABC):
# #     """
# #     Universal template for all MetaFlow agents
# #     Handles common functionality while allowing specific implementations
# #     """
    
# #     def __init__(self, agent_config: Dict[str, Any], workflow_context: Dict[str, Any]):
# #         """
# #         Initialize base agent with configuration from BA_enhanced.json
        
# #         Args:
# #             agent_config: Individual agent configuration from JSON
# #             workflow_context: Overall workflow metadata and shared resources
# #         """
# #         # 1. Agent Identity
# #         self.agent_id = agent_config['agent_id']
# #         self.agent_name = agent_config['agent_name']
# #         self.position = agent_config['position']
# #         self.identity = agent_config['identity']
        
# #         # 2. MCP Tool Access
# #         self.tools = agent_config.get('tools', [])
# #         self.mcp_executor = MCPToolExecutor(workflow_context.get('claude_cwd', Path(r"C:\Users\manis")))
        
# #         # 3. Input Processing
# #         self.data_interface = agent_config['data_interface']
# #         self.input_types = self.data_interface['input']['types']
# #         self.output_types = self.data_interface['output']['types']
        
# #         # 4. Output Formatting
# #         self.output_delivery = self.data_interface['output']['delivery']
        
# #         # 5. State Management
# #         self.state_config = agent_config['state']
# #         self.local_state = {}
# #         self.workflow_state = workflow_context.get('shared_state', {})
        
# #         # 6. Communication Interface
# #         self.interface_config = agent_config['interface']
# #         self.dependencies = self.interface_config['dependencies']
# #         self.outputs_to = self.interface_config['outputs_to']
# #         self.error_strategy = self.interface_config['error_strategy']
# #         self.message_queue = asyncio.Queue()
        
# #         # LLM Configuration
# #         self.llm_config = agent_config['llm_config']
# #         self.reasoning_type = self.llm_config['reasoning']  # 'function-calling' or 'ReAct'
        
# #         # Initialize local LLM connection
# #         self.local_llm_url = workflow_context.get('llm_url', "http://localhost:1234/v1/chat/completions")
        
# #         logger.info(f"✅ Initialized {self.agent_name} (ID: {self.agent_id})")
# #         logger.info(f"   Tools: {[t['name'] for t in self.tools]}")
# #         logger.info(f"   Dependencies: {self.dependencies}")
    
# #     @abstractmethod
# #     async def execute(self, input_data: Any) -> Any:
# #         """
# #         Main execution method - must be implemented by each specific agent
        
# #         Args:
# #             input_data: Input from previous agent or initial data
            
# #         Returns:
# #             Processed output for next agent
# #         """
# #         pass
    
# #     async def run(self, input_data: Any = None) -> AgentState:
# #         """
# #         Wrapper method that handles common execution logic
# #         """
# #         logger.info(f"🚀 {self.agent_name} starting execution...")
        
# #         # Initialize state
# #         state = AgentState(
# #             agent_id=self.agent_id,
# #             status='running',
# #             input_data=input_data,
# #             start_time=datetime.now()
# #         )
        
# #         try:
# #             # Validate input
# #             if not self._validate_input(input_data):
# #                 raise ValueError(f"Invalid input type for {self.agent_name}")
            
# #             # Execute agent-specific logic
# #             output = await self.execute(input_data)
            
# #             # Format output
# #             formatted_output = self._format_output(output)
            
# #             # Update state
# #             state.output_data = formatted_output
# #             state.status = 'completed'
# #             state.end_time = datetime.now()
            
# #             logger.info(f"✅ {self.agent_name} completed successfully")
            
# #         except Exception as e:
# #             state.status = 'failed'
# #             state.error = str(e)
# #             state.end_time = datetime.now()
            
# #             logger.error(f"❌ {self.agent_name} failed: {e}")
            
# #             # Handle error based on strategy
# #             if self.error_strategy == 'retry':
# #                 logger.info(f"🔄 Retrying {self.agent_name}...")
# #                 # Implement retry logic here
            
# #         return state
    
# #     def _validate_input(self, input_data: Any) -> bool:
# #         """Validate input data against expected types"""
# #         if input_data is None:
# #             return 'null' in self.input_types or not self.input_types
        
# #         if isinstance(input_data, dict) and 'json' in self.input_types:
# #             return True
# #         if isinstance(input_data, str) and 'text' in self.input_types:
# #             return True
        
# #         return False
    
# #     def _format_output(self, output: Any) -> Any:
# #         """Format output according to interface requirements"""
# #         if 'json' in self.output_types and isinstance(output, str):
# #             try:
# #                 return json.loads(output)
# #             except:
# #                 return {"text": output}
        
# #         return output
    
# #     async def call_local_llm(self, prompt: str) -> str:
# #         """
# #         Call local LLM (Qwen 2.5 14B) for reasoning
        
# #         This is where agents use the local Qwen model for decision-making,
# #         while Claude Code is only used for tool execution to minimize tokens.
# #         """
# #         try:
# #             # Prepare messages based on reasoning type
# #             if self.reasoning_type == 'function-calling':
# #                 messages = [
# #                     {"role": "system", "content": f"You are {self.agent_name}. {self.identity['role']}"},
# #                     {"role": "user", "content": prompt}
# #                 ]
# #             else:  # ReAct
# #                 messages = [
# #                     {"role": "system", "content": f"You are {self.agent_name}. {self.identity['role']} Use the ReAct pattern: Thought, Action, Observation, Result."},
# #                     {"role": "user", "content": prompt}
# #                 ]
            
# #             response = requests.post(
# #                 self.local_llm_url,
# #                 json={
# #                     "model": self.llm_config['model'],  # qwen2.5-coder-14b-instruct
# #                     "messages": messages,
# #                     "temperature": self.llm_config['params']['temperature'],
# #                     "max_tokens": self.llm_config['params']['max_tokens']
# #                 },
# #                 timeout=60
# #             )
            
# #             if response.status_code == 200:
# #                 return response.json()['choices'][0]['message']['content']
# #             else:
# #                 raise Exception(f"LLM call failed: {response.status_code}")
                
# #         except Exception as e:
# #             logger.error(f"Failed to call local LLM: {e}")
# #             raise
    
# #     async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
# #         """
# #         Execute an MCP tool via Claude Code
# #         """
# #         # Find the full tool info
# #         tool_info = next((t for t in self.tools if t['name'] == tool_name), None)
# #         if not tool_info:
# #             raise ValueError(f"Tool {tool_name} not found in agent's tool list")
        
# #         return await self.mcp_executor.execute_tool(tool_info, parameters)
    
# #     async def send_message(self, receiver_id: str, message_type: str, content: Any):
# #         """Send message to another agent"""
# #         message = AgentMessage(
# #             sender_id=self.agent_id,
# #             receiver_id=receiver_id,
# #             message_type=message_type,
# #             content=content
# #         )
# #         # In real implementation, this would use a message broker
# #         logger.info(f"📧 {self.agent_name} -> {receiver_id}: {message_type}")
        
# #     def update_shared_state(self, key: str, value: Any):
# #         """Update shared workflow state"""
# #         self.workflow_state[key] = value
# #         logger.info(f"📝 {self.agent_name} updated shared state: {key}")


# # class MCPToolExecutor:
# #     """
# #     Handles execution of MCP tools via Claude Code
# #     """
    
# #     def __init__(self, claude_cwd: Path):
# #         self.claude_cwd = claude_cwd
# #         self.claude_cmd = [
# #             "powershell.exe",
# #             "-NoLogo",
# #             "-NoProfile",
# #             "-Command",
# #             "claude"
# #         ]
# #         self.timeout = 300
    
# #     async def execute_tool(self, tool_info: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
# #         """
# #         Execute MCP tool by generating natural language prompt for Claude
        
# #         Args:
# #             tool_info: Tool information including name and server
# #             parameters: Parameters to pass to the tool
            
# #         Returns:
# #             Execution result
# #         """
# #         tool_name = tool_info['name']
        
# #         # Create natural language prompt for Claude Code
# #         param_str = ", ".join([f"{k}='{v}'" for k, v in parameters.items()])
# #         prompt = f"Use the {tool_name} tool with these parameters: {param_str}"
        
# #         logger.info(f"🔧 Executing tool: {tool_name}")
# #         logger.info(f"   Prompt: {prompt}")
        
# #         try:
# #             # Execute via subprocess
# #             result = await asyncio.get_event_loop().run_in_executor(
# #                 None, 
# #                 self._execute_claude_command, 
# #                 prompt
# #             )
            
# #             # Parse result
# #             return self._parse_tool_result(result, tool_name)
            
# #         except Exception as e:
# #             logger.error(f"Tool execution failed: {e}")
# #             return {
# #                 "success": False,
# #                 "error": str(e),
# #                 "tool": tool_name
# #             }
    
# #     def _execute_claude_command(self, prompt: str) -> str:
# #         """Execute Claude command synchronously"""
# #         # Write prompt to input file
# #         input_file = self.claude_cwd / "tool_input.txt"
# #         with open(input_file, 'w', encoding='utf-8') as f:
# #             f.write(prompt)
        
# #         # Execute Claude
# #         proc = subprocess.Popen(
# #             self.claude_cmd,
# #             stdin=subprocess.PIPE,
# #             stdout=subprocess.PIPE,
# #             stderr=subprocess.PIPE,
# #             cwd=str(self.claude_cwd),
# #             text=True,
# #             encoding='utf-8'
# #         )
        
# #         # Feed input
# #         with open(input_file, 'r', encoding='utf-8') as f:
# #             input_data = f.read()
        
# #         stdout, stderr = proc.communicate(input=input_data, timeout=self.timeout)
        
# #         # Clean up
# #         if input_file.exists():
# #             input_file.unlink()
        
# #         return stdout
    
# #     def _parse_tool_result(self, raw_output: str, tool_name: str) -> Dict[str, Any]:
# #         """Parse tool execution result from Claude output"""
# #         # Basic parsing - can be enhanced based on actual output patterns
# #         if "error" in raw_output.lower() or "failed" in raw_output.lower():
# #             return {
# #                 "success": False,
# #                 "output": raw_output,
# #                 "tool": tool_name
# #             }
        
# #         return {
# #             "success": True,
# #             "output": raw_output,
# #             "tool": tool_name
# #         }


# # class DynamicAgent(BaseAgent):
# #     """
# #     Generic agent implementation that can handle any agent type
# #     Uses the local LLM to determine actions based on role
# #     """
    
# #     async def execute(self, input_data: Any) -> Any:
# #         """
# #         Dynamic execution based on agent role and available tools
# #         """
# #         # Build context for LLM
# #         context = {
# #             "role": self.identity['role'],
# #             "input": input_data,
# #             "available_tools": [t['name'] for t in self.tools],
# #             "position": self.position,
# #             "outputs_to": self.outputs_to
# #         }
        
# #         # Create prompt for local LLM
# #         prompt = self._build_execution_prompt(context)
        
# #         # Get LLM response
# #         llm_response = await self.call_local_llm(prompt)
        
# #         # Parse and execute any tool calls
# #         result = await self._process_llm_response(llm_response)
        
# #         return result
    
# #     def _build_execution_prompt(self, context: Dict[str, Any]) -> str:
# #         """Build prompt for LLM based on agent context"""
# #         prompt = f"""
# # You are {self.agent_name} with the following role:
# # {context['role']}

# # Input received: {json.dumps(context['input'], indent=2) if isinstance(context['input'], dict) else context['input']}

# # Available tools: {', '.join(context['available_tools'])}

# # Based on your role and the input, determine what actions to take.
# # If you need to use tools, respond in this format:
# # TOOL_CALL: tool_name
# # PARAMETERS: 
# #   param1: value1
# #   param2: value2

# # After any tool calls, provide your final output that will be passed to the next agent.

# # Remember: You are agent {context['position']} in the workflow. Your output goes to: {context['outputs_to']}
# # """
# #         return prompt
    
# #     async def _process_llm_response(self, response: str) -> Any:
# #         """Process LLM response and execute any tool calls"""
# #         lines = response.split('\n')
# #         final_output = []
        
# #         i = 0
# #         while i < len(lines):
# #             line = lines[i].strip()
            
# #             # Check for tool call
# #             if line.startswith("TOOL_CALL:"):
# #                 tool_name = line.split(":", 1)[1].strip()
# #                 parameters = {}
                
# #                 # Parse parameters
# #                 i += 1
# #                 if i < len(lines) and lines[i].strip() == "PARAMETERS:":
# #                     i += 1
# #                     while i < len(lines) and lines[i].strip() and not lines[i].startswith("TOOL_CALL:"):
# #                         param_line = lines[i].strip()
# #                         if ':' in param_line:
# #                             key, value = param_line.split(':', 1)
# #                             parameters[key.strip()] = value.strip()
# #                         i += 1
                
# #                 # Execute tool
# #                 result = await self.execute_tool(tool_name, parameters)
# #                 final_output.append(result)
# #             else:
# #                 if line and not line.startswith("PARAMETERS:"):
# #                     final_output.append(line)
# #                 i += 1
        
# #         # Return appropriate format
# #         if len(final_output) == 1:
# #             return final_output[0]
# #         else:
# #             return '\n'.join(str(item) for item in final_output)


# # class AgentFactory:
# #     """
# #     Factory for creating agents from BA_enhanced.json
# #     """
    
# #     def __init__(self, llm_url: str = "http://localhost:1234/v1/chat/completions", output_dir: str = None):
# #         self.llm_url = llm_url
# #         self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "created_agents"
# #         self.workflow_context = {
# #             'llm_url': llm_url,
# #             'claude_cwd': Path(r"C:\Users\manis"),
# #             'shared_state': {}
# #         }
    
# #     def create_agent(self, agent_config: Dict[str, Any]) -> BaseAgent:
# #         """
# #         Create an agent instance based on configuration
        
# #         Args:
# #             agent_config: Agent configuration from BA_enhanced.json
            
# #         Returns:
# #             Instantiated agent
# #         """
# #         # For now, all agents use the DynamicAgent implementation
# #         # In future, we could have specialized classes for certain agent types
        
# #         agent = DynamicAgent(agent_config, self.workflow_context)
# #         return agent
    
# #     def create_agent_file(self, agent_config: Dict[str, Any], workflow_id: str) -> Path:
# #         """
# #         Create a standalone Python file for an individual agent
        
# #         Args:
# #             agent_config: Agent configuration from BA_enhanced.json
# #             workflow_id: Workflow identifier for organization
            
# #         Returns:
# #             Path to created agent file
# #         """
# #         # Ensure output directory exists
# #         agent_dir = self.output_dir / workflow_id
# #         agent_dir.mkdir(parents=True, exist_ok=True)
        
# #         # Clean agent name for filename
# #         agent_name = agent_config['agent_name'].replace('*', '').replace(' ', '_').lower()
# #         filename = f"{agent_config['agent_id']}_{agent_name}.py"
# #         filepath = agent_dir / filename
        
# #         # Generate agent code
# #         agent_code = self._generate_agent_code(agent_config)
        
# #         # Write to file
# #         with open(filepath, 'w', encoding='utf-8') as f:
# #             f.write(agent_code)
        
# #         logger.info(f"📄 Created agent file: {filepath}")
# #         return filepath
    
# #     def _generate_agent_code(self, agent_config: Dict[str, Any]) -> str:
# #         """
# #         Generate standalone Python code for an agent
# #         """
# #         agent_name = agent_config['agent_name'].replace('*', '').strip()
# #         class_name = ''.join(word.capitalize() for word in agent_name.replace('-', ' ').replace('_', ' ').split())
        
# #         code = f'''#!/usr/bin/env python3
# # # -*- coding: utf-8 -*-
# # """
# # {agent_name} - Auto-generated agent for MetaFlow
# # Position: {agent_config['position']}
# # Role: {agent_config['identity']['role']}
# # """

# # from pathlib import Path
# # from typing import Dict, List, Any, Optional
# # import json
# # import logging
# # import asyncio
# # from datetime import datetime

# # # Import base agent (this would need to be in Python path)
# # # from agent_creation_factory import BaseAgent, MCPToolExecutor

# # logger = logging.getLogger(__name__)


# # class {class_name}:
# #     """
# #     {agent_config['identity']['description']}
# #     """
    
# #     def __init__(self):
# #         # Agent Identity
# #         self.agent_id = "{agent_config['agent_id']}"
# #         self.agent_name = "{agent_config['agent_name']}"
# #         self.position = {agent_config['position']}
        
# #         # Role Definition
# #         self.role = """{agent_config['identity']['role']}"""
# #         self.agent_type = "{agent_config['identity']['agent_type']}"
        
# #         # Tools Configuration
# #         self.tools = {json.dumps(agent_config['tools'], indent=8)}
        
# #         # Data Interface
# #         self.input_types = {agent_config['data_interface']['input']['types']}
# #         self.output_types = {agent_config['data_interface']['output']['types']}
# #         self.output_delivery = "{agent_config['data_interface']['output']['delivery']}"
        
# #         # LLM Configuration
# #         self.llm_config = {{
# #             "provider": "{agent_config['llm_config']['provider']}",
# #             "model": "{agent_config['llm_config']['model']}",
# #             "reasoning": "{agent_config['llm_config']['reasoning']}",
# #             "temperature": {agent_config['llm_config']['params']['temperature']},
# #             "max_tokens": {agent_config['llm_config']['params']['max_tokens']}
# #         }}
        
# #         # Dependencies and Outputs
# #         self.dependencies = {agent_config['interface']['dependencies']}
# #         self.outputs_to = {agent_config['interface']['outputs_to']}
# #         self.error_strategy = "{agent_config['interface']['error_strategy']}"
        
# #         logger.info(f"✅ Initialized {{self.agent_name}} (ID: {{self.agent_id}})")
    
# #     async def execute(self, input_data: Any) -> Any:
# #         """
# #         Execute the agent's main task
        
# #         Args:
# #             input_data: Input from previous agent or initial data
            
# #         Returns:
# #             Processed output for next agent
# #         """
# #         logger.info(f"🚀 {{self.agent_name}} starting execution...")
        
# #         try:
# #             # Agent-specific logic based on role
# #             result = await self._process_task(input_data)
            
# #             logger.info(f"✅ {{self.agent_name}} completed successfully")
# #             return result
            
# #         except Exception as e:
# #             logger.error(f"❌ {{self.agent_name}} failed: {{e}}")
# #             raise
    
# #     async def _process_task(self, input_data: Any) -> Any:
# #         """
# #         Main processing logic for {agent_name}
        
# #         This method should:
# #         1. Analyze the input based on the agent's role
# #         2. Use LLM for reasoning if needed
# #         3. Execute required tools
# #         4. Format and return the output
# #         """
# #         # TODO: Implement specific logic based on role:
# #         # {agent_config['identity']['role']}
        
# #         # For now, return a placeholder
# #         return {{
# #             "agent": self.agent_name,
# #             "status": "processed",
# #             "input_received": input_data,
# #             "timestamp": datetime.now().isoformat(),
# #             "next_agent": self.outputs_to[0] if self.outputs_to else None
# #         }}
    
# #     def get_info(self) -> Dict[str, Any]:
# #         """Get agent information"""
# #         return {{
# #             "agent_id": self.agent_id,
# #             "agent_name": self.agent_name,
# #             "position": self.position,
# #             "role": self.role,
# #             "tools": [tool["name"] for tool in self.tools],
# #             "dependencies": self.dependencies,
# #             "outputs_to": self.outputs_to
# #         }}


# # # Standalone execution for testing
# # if __name__ == "__main__":
# #     async def test_agent():
# #         agent = {class_name}()
# #         print(f"Agent Info: {{json.dumps(agent.get_info(), indent=2)}}")
        
# #         # Test execution with sample input
# #         test_input = {{"test": "data", "timestamp": datetime.now().isoformat()}}
# #         result = await agent.execute(test_input)
# #         print(f"Execution Result: {{json.dumps(result, indent=2, default=str)}}")
    
# #     asyncio.run(test_agent())
# # '''
        
# #         return code
    
# #     def create_workflow(self, ba_enhanced_path: str) -> 'WorkflowOrchestrator':
# #         """
# #         Create complete workflow from BA_enhanced.json
        
# #         Args:
# #             ba_enhanced_path: Path to BA_enhanced.json file
            
# #         Returns:
# #             WorkflowOrchestrator instance
# #         """
# #         # Load configuration
# #         with open(ba_enhanced_path, 'r', encoding='utf-8') as f:
# #             workflow_data = json.load(f)
        
# #         workflow_id = workflow_data['workflow_metadata']['workflow_id']
        
# #         # Create individual agent files
# #         logger.info(f"📁 Creating agent files in: {self.output_dir / workflow_id}")
# #         for agent_config in workflow_data['agents']:
# #             self.create_agent_file(agent_config, workflow_id)
        
# #         # Create workflow documentation
# #         self._create_workflow_docs(workflow_data, workflow_id)
        
# #         # Create agents for runtime
# #         agents = {}
# #         for agent_config in workflow_data['agents']:
# #             agent = self.create_agent(agent_config)
# #             agents[agent.agent_id] = agent
        
# #         # Create orchestrator
# #         orchestrator = WorkflowOrchestrator(
# #             agents=agents,
# #             workflow_metadata=workflow_data['workflow_metadata'],
# #             orchestration_config=workflow_data['orchestration']
# #         )
        
# #         return orchestrator
    
# #     def _create_workflow_docs(self, workflow_data: Dict, workflow_id: str):
# #         """Create workflow documentation file"""
# #         doc_path = self.output_dir / workflow_id / "workflow_documentation.md"
        
# #         doc_content = f"""# Workflow Documentation: {workflow_id}

# # ## Overview
# # - **Domain**: {workflow_data['workflow_metadata']['domain']}
# # - **Architecture**: {workflow_data['workflow_metadata']['selected_architecture']}
# # - **Total Agents**: {workflow_data['workflow_metadata']['total_agents']}
# # - **Estimated Execution Time**: {workflow_data['workflow_metadata']['estimated_execution_time']}

# # ## Agent Pipeline

# # """
# #         for agent in workflow_data['agents']:
# #             doc_content += f"""### {agent['position']}. {agent['agent_name']}
# # - **ID**: {agent['agent_id']}
# # - **Role**: {agent['identity']['role']}
# # - **Tools**: {', '.join([t['name'] for t in agent['tools']])}
# # - **Dependencies**: {', '.join(agent['interface']['dependencies']) or 'None'}
# # - **Outputs To**: {', '.join(agent['interface']['outputs_to']) or 'None'}

# # """
        
# #         doc_content += f"""## Orchestration Pattern
# # - **Type**: {workflow_data['orchestration']['pattern']}
# # - **Connections**: {len(workflow_data['orchestration']['connections'])} connections

# # ## Usage
# # ```python
# # from agent_creation_factory import AgentFactory

# # factory = AgentFactory()
# # workflow = factory.create_workflow("{workflow_id}/BA_enhanced.json")
# # result = await workflow.execute(initial_input)
# # ```
# # """
        
# #         with open(doc_path, 'w', encoding='utf-8') as f:
# #             f.write(doc_content)
        
# #         logger.info(f"📝 Created workflow documentation: {doc_path}")


# # class WorkflowOrchestrator:
# #     """
# #     Manages workflow execution based on selected architecture pattern
# #     """
    
# #     def __init__(self, agents: Dict[str, BaseAgent], workflow_metadata: Dict, orchestration_config: Dict):
# #         self.agents = agents
# #         self.metadata = workflow_metadata
# #         self.orchestration = orchestration_config
# #         self.pattern = orchestration_config['pattern']
# #         self.connections = orchestration_config['connections']
        
# #         # State tracking
# #         self.agent_states = {
# #             agent_id: AgentState(agent_id=agent_id, status='ready')
# #             for agent_id in agents.keys()
# #         }
        
# #         logger.info(f"📊 Workflow Orchestrator initialized")
# #         logger.info(f"   Pattern: {self.pattern}")
# #         logger.info(f"   Total agents: {len(self.agents)}")
    
# #     async def execute(self, initial_input: Any = None) -> Dict[str, Any]:
# #         """
# #         Execute the workflow based on the orchestration pattern
        
# #         Note: The workflow specification in BA_enhanced.json already contains
# #         all necessary context from the user's original prompt. The agents
# #         will work based on their defined roles and the workflow structure.
        
# #         Args:
# #             initial_input: Optional initial data for the first agent.
# #                          If not provided, agents will work based on their roles.
# #         """
# #         logger.info(f"🎯 Starting workflow execution: {self.metadata['workflow_id']}")
# #         logger.info(f"   Architecture: {self.metadata['selected_architecture']}")
# #         logger.info(f"   Domain: {self.metadata['domain']}")
        
# #         # If no initial input provided, create a minimal context
# #         if initial_input is None:
# #             initial_input = {
# #                 "workflow_id": self.metadata['workflow_id'],
# #                 "execution_start": datetime.now().isoformat(),
# #                 "note": "Agents will execute based on their predefined roles from BA_enhanced.json"
# #             }
        
# #         start_time = datetime.now()
        
# #         try:
# #             if "pipeline" in self.pattern.lower() or "sequential" in self.pattern.lower():
# #                 result = await self._execute_pipeline(initial_input)
# #             elif "event" in self.pattern.lower():
# #                 result = await self._execute_event_driven(initial_input)
# #             elif "hub" in self.pattern.lower():
# #                 result = await self._execute_hub_spoke(initial_input)
# #             elif "hierarchical" in self.pattern.lower():
# #                 result = await self._execute_hierarchical(initial_input)
# #             elif "collaborative" in self.pattern.lower():
# #                 result = await self._execute_collaborative(initial_input)
# #             else:
# #                 # Default to pipeline
# #                 result = await self._execute_pipeline(initial_input)
            
# #             end_time = datetime.now()
# #             duration = (end_time - start_time).total_seconds()
            
# #             logger.info(f"✅ Workflow completed in {duration:.2f} seconds")
            
# #             return {
# #                 "success": True,
# #                 "workflow_id": self.metadata['workflow_id'],
# #                 "duration": duration,
# #                 "result": result,
# #                 "agent_states": self._get_states_summary()
# #             }
            
# #         except Exception as e:
# #             logger.error(f"❌ Workflow failed: {e}")
# #             return {
# #                 "success": False,
# #                 "workflow_id": self.metadata['workflow_id'],
# #                 "error": str(e),
# #                 "agent_states": self._get_states_summary()
# #             }
    
# #     async def _execute_pipeline(self, initial_input: Any) -> Any:
# #         """Execute agents in sequential pipeline"""
# #         current_input = initial_input
        
# #         # Get agents sorted by position
# #         sorted_agents = sorted(self.agents.values(), key=lambda a: a.position)
        
# #         for agent in sorted_agents:
# #             logger.info(f"🔄 Executing agent {agent.position}: {agent.agent_name}")
            
# #             # Run agent
# #             state = await agent.run(current_input)
# #             self.agent_states[agent.agent_id] = state
            
# #             if state.status == 'failed':
# #                 raise Exception(f"Agent {agent.agent_name} failed: {state.error}")
            
# #             # Pass output to next agent
# #             current_input = state.output_data
        
# #         return current_input
    
# #     async def _execute_event_driven(self, initial_input: Any) -> Any:
# #         """Execute event-driven architecture"""
# #         # TODO: Implement event-driven execution
# #         # For now, fall back to pipeline
# #         logger.warning("Event-driven execution not yet implemented, using pipeline")
# #         return await self._execute_pipeline(initial_input)
    
# #     async def _execute_hub_spoke(self, initial_input: Any) -> Any:
# #         """Execute hub-and-spoke architecture"""
# #         # TODO: Implement hub-spoke execution
# #         # For now, fall back to pipeline
# #         logger.warning("Hub-spoke execution not yet implemented, using pipeline")
# #         return await self._execute_pipeline(initial_input)
    
# #     async def _execute_hierarchical(self, initial_input: Any) -> Any:
# #         """Execute hierarchical architecture"""
# #         # TODO: Implement hierarchical execution
# #         # For now, fall back to pipeline
# #         logger.warning("Hierarchical execution not yet implemented, using pipeline")
# #         return await self._execute_pipeline(initial_input)
    
# #     async def _execute_collaborative(self, initial_input: Any) -> Any:
# #         """Execute collaborative architecture"""
# #         # TODO: Implement collaborative execution
# #         # For now, fall back to pipeline
# #         logger.warning("Collaborative execution not yet implemented, using pipeline")
# #         return await self._execute_pipeline(initial_input)
    
# #     def _get_states_summary(self) -> Dict[str, Dict]:
# #         """Get summary of all agent states"""
# #         summary = {}
# #         for agent_id, state in self.agent_states.items():
# #             summary[agent_id] = {
# #                 "status": state.status,
# #                 "error": state.error,
# #                 "duration": (state.end_time - state.start_time).total_seconds() if state.end_time and state.start_time else None
# #             }
# #         return summary


# # # Example usage
# # async def main():
# #     """
# #     Agent Factory - Creates agents from BA_enhanced.json
    
# #     The workflow is:
# #     1. User Prompt → Base Agent (Qwen 2.5 14B) → BA_op.json
# #     2. BA_op.json → Tool Mapper → BA_enhanced.json
# #     3. BA_enhanced.json → Agent Factory → Created Agents
    
# #     This factory only needs BA_enhanced.json as input.
# #     """
# #     import sys
    
# #     if len(sys.argv) < 2:
# #         print("Usage: python agent_creation_factory.py <path_to_BA_enhanced.json>")
# #         print("\nThis factory creates agents from the enhanced workflow specification.")
# #         print("The user prompt has already been processed by Base Agent and Tool Mapper.")
# #         sys.exit(1)
    
# #     ba_enhanced_path = sys.argv[1]
    
# #     print(f"\n🏭 MetaFlow Agent Factory")
# #     print(f"="*60)
# #     print(f"📄 Input: {ba_enhanced_path}")
# #     print(f"🤖 LLM: Qwen 2.5 14B (local)")
# #     print(f"="*60)
    
# #     # Initialize factory
# #     factory = AgentFactory()
    
# #     # Create workflow from BA_enhanced.json
# #     print("\n⚙️  Creating workflow and agents...")
# #     workflow = factory.create_workflow(ba_enhanced_path)
    
# #     print(f"\n✅ Workflow created successfully!")
# #     print(f"📁 Agent files saved to: {factory.output_dir}")
    
# #     # The workflow is now ready to execute
# #     # In production, this would be triggered by external events or scheduler
# #     print("\n🎯 Workflow is ready for execution")
# #     print("Agents will process tasks according to the workflow specification")
    
# #     # Optional: Show workflow summary
# #     with open(ba_enhanced_path, 'r') as f:
# #         data = json.load(f)
    
# #     print(f"\n📊 Workflow Summary:")
# #     print(f"   - Workflow ID: {data['workflow_metadata']['workflow_id']}")
# #     print(f"   - Domain: {data['workflow_metadata']['domain']}")
# #     print(f"   - Architecture: {data['workflow_metadata']['selected_architecture']}")
# #     print(f"   - Total Agents: {data['workflow_metadata']['total_agents']}")
# #     print(f"   - Orchestration: {data['orchestration']['pattern']}")


# # if __name__ == "__main__":
# #     # Run factory
# #     asyncio.run(main())


# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# Agent Creation Factory for MetaFlow Platform
# Creates and manages LangChain agents based on BA_enhanced.json specifications

# IMPORTANT: Two-phase operation:
# 1. GENERATION PHASE (No LLM needed): Creates Python files from BA_enhanced.json templates
# 2. EXECUTION PHASE (Requires LLM): Agents use Qwen 2.5 14B for reasoning during runtime

# The factory can generate agent files without LM Studio running, but agents 
# need LM Studio running when they actually execute tasks.
# """

# import json
# import subprocess
# import asyncio
# import logging
# from pathlib import Path
# from typing import Dict, List, Any, Optional, Tuple
# from abc import ABC, abstractmethod
# from datetime import datetime
# from dataclasses import dataclass, field
# from concurrent.futures import ThreadPoolExecutor
# import requests

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)


# @dataclass
# class AgentMessage:
#     """Message structure for inter-agent communication"""
#     sender_id: str
#     receiver_id: str
#     message_type: str  # 'data', 'status', 'error', 'request'
#     content: Any
#     timestamp: datetime = field(default_factory=datetime.now)
#     requires_response: bool = False


# @dataclass
# class AgentState:
#     """Shared state for agent execution"""
#     agent_id: str
#     status: str  # 'ready', 'running', 'completed', 'failed', 'waiting'
#     input_data: Any = None
#     output_data: Any = None
#     error: Optional[str] = None
#     start_time: Optional[datetime] = None
#     end_time: Optional[datetime] = None
#     dependencies_met: bool = False


# class BaseAgent(ABC):
#     """
#     Universal template for all MetaFlow agents
#     Handles common functionality while allowing specific implementations
#     """
    
#     def __init__(self, agent_config: Dict[str, Any], workflow_context: Dict[str, Any]):
#         """
#         Initialize base agent with configuration from BA_enhanced.json
        
#         Args:
#             agent_config: Individual agent configuration from JSON
#             workflow_context: Overall workflow metadata and shared resources
#         """
#         # 1. Agent Identity
#         self.agent_id = agent_config['agent_id']
#         self.agent_name = agent_config['agent_name']
#         self.position = agent_config['position']
#         self.identity = agent_config['identity']
        
#         # 2. MCP Tool Access
#         self.tools = agent_config.get('tools', [])
#         self.mcp_executor = MCPToolExecutor(workflow_context.get('claude_cwd', Path(r"C:\Users\manis")))
        
#         # 3. Input Processing
#         self.data_interface = agent_config['data_interface']
#         self.input_types = self.data_interface['input']['types']
#         self.output_types = self.data_interface['output']['types']
        
#         # 4. Output Formatting
#         self.output_delivery = self.data_interface['output']['delivery']
        
#         # 5. State Management
#         self.state_config = agent_config['state']
#         self.local_state = {}
#         self.workflow_state = workflow_context.get('shared_state', {})
        
#         # 6. Communication Interface
#         self.interface_config = agent_config['interface']
#         self.dependencies = self.interface_config['dependencies']
#         self.outputs_to = self.interface_config['outputs_to']
#         self.error_strategy = self.interface_config['error_strategy']
#         self.message_queue = asyncio.Queue()
        
#         # LLM Configuration
#         self.llm_config = agent_config['llm_config']
#         self.reasoning_type = self.llm_config['reasoning']  # 'function-calling' or 'ReAct'
        
#         # Initialize local LLM connection
#         self.local_llm_url = workflow_context.get('llm_url', "http://localhost:1234/v1/chat/completions")
        
#         logger.info(f"✅ Initialized {self.agent_name} (ID: {self.agent_id})")
#         logger.info(f"   Tools: {[t['name'] for t in self.tools]}")
#         logger.info(f"   Dependencies: {self.dependencies}")
    
#     @abstractmethod
#     async def execute(self, input_data: Any) -> Any:
#         """
#         Main execution method - must be implemented by each specific agent
        
#         Args:
#             input_data: Input from previous agent or initial data
            
#         Returns:
#             Processed output for next agent
#         """
#         pass
    
#     async def run(self, input_data: Any = None) -> AgentState:
#         """
#         Wrapper method that handles common execution logic
#         """
#         logger.info(f"🚀 {self.agent_name} starting execution...")
        
#         # Initialize state
#         state = AgentState(
#             agent_id=self.agent_id,
#             status='running',
#             input_data=input_data,
#             start_time=datetime.now()
#         )
        
#         try:
#             # Validate input
#             if not self._validate_input(input_data):
#                 raise ValueError(f"Invalid input type for {self.agent_name}")
            
#             # Execute agent-specific logic
#             output = await self.execute(input_data)
            
#             # Format output
#             formatted_output = self._format_output(output)
            
#             # Update state
#             state.output_data = formatted_output
#             state.status = 'completed'
#             state.end_time = datetime.now()
            
#             logger.info(f"✅ {self.agent_name} completed successfully")
            
#         except Exception as e:
#             state.status = 'failed'
#             state.error = str(e)
#             state.end_time = datetime.now()
            
#             logger.error(f"❌ {self.agent_name} failed: {e}")
            
#             # Handle error based on strategy
#             if self.error_strategy == 'retry':
#                 logger.info(f"🔄 Retrying {self.agent_name}...")
#                 # Implement retry logic here
            
#         return state
    
#     def _validate_input(self, input_data: Any) -> bool:
#         """Validate input data against expected types"""
#         if input_data is None:
#             return 'null' in self.input_types or not self.input_types
        
#         if isinstance(input_data, dict) and 'json' in self.input_types:
#             return True
#         if isinstance(input_data, str) and 'text' in self.input_types:
#             return True
        
#         return False
    
#     def _format_output(self, output: Any) -> Any:
#         """Format output according to interface requirements"""
#         if 'json' in self.output_types and isinstance(output, str):
#             try:
#                 return json.loads(output)
#             except:
#                 return {"text": output}
        
#         return output
    
#     async def call_local_llm(self, prompt: str) -> str:
#         """
#         Call local LLM (Qwen 2.5 14B) for reasoning
        
#         This is where agents use the local Qwen model for decision-making,
#         while Claude Code is only used for tool execution to minimize tokens.
#         """
#         try:
#             # Prepare messages based on reasoning type
#             if self.reasoning_type == 'function-calling':
#                 messages = [
#                     {"role": "system", "content": f"You are {self.agent_name}. {self.identity['role']}"},
#                     {"role": "user", "content": prompt}
#                 ]
#             else:  # ReAct
#                 messages = [
#                     {"role": "system", "content": f"You are {self.agent_name}. {self.identity['role']} Use the ReAct pattern: Thought, Action, Observation, Result."},
#                     {"role": "user", "content": prompt}
#                 ]
            
#             response = requests.post(
#                 self.local_llm_url,
#                 json={
#                     "model": self.llm_config['model'],  # qwen2.5-coder-14b-instruct
#                     "messages": messages,
#                     "temperature": self.llm_config['params']['temperature'],
#                     "max_tokens": self.llm_config['params']['max_tokens']
#                 },
#                 timeout=60
#             )
            
#             if response.status_code == 200:
#                 return response.json()['choices'][0]['message']['content']
#             else:
#                 raise Exception(f"LLM call failed: {response.status_code}")
                
#         except Exception as e:
#             logger.error(f"Failed to call local LLM: {e}")
#             raise
    
#     async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         Execute an MCP tool via Claude Code
#         """
#         # Find the full tool info
#         tool_info = next((t for t in self.tools if t['name'] == tool_name), None)
#         if not tool_info:
#             raise ValueError(f"Tool {tool_name} not found in agent's tool list")
        
#         return await self.mcp_executor.execute_tool(tool_info, parameters)
    
#     async def send_message(self, receiver_id: str, message_type: str, content: Any):
#         """Send message to another agent"""
#         message = AgentMessage(
#             sender_id=self.agent_id,
#             receiver_id=receiver_id,
#             message_type=message_type,
#             content=content
#         )
#         # In real implementation, this would use a message broker
#         logger.info(f"📧 {self.agent_name} -> {receiver_id}: {message_type}")
        
#     def update_shared_state(self, key: str, value: Any):
#         """Update shared workflow state"""
#         self.workflow_state[key] = value
#         logger.info(f"📝 {self.agent_name} updated shared state: {key}")


# class MCPToolExecutor:
#     """
#     Handles execution of MCP tools via Claude Code
#     """
    
#     def __init__(self, claude_cwd: Path):
#         self.claude_cwd = claude_cwd
#         self.claude_cmd = [
#             "powershell.exe",
#             "-NoLogo",
#             "-NoProfile",
#             "-Command",
#             "claude"
#         ]
#         self.timeout = 300
    
#     async def execute_tool(self, tool_info: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         Execute MCP tool by generating natural language prompt for Claude
        
#         Args:
#             tool_info: Tool information including name and server
#             parameters: Parameters to pass to the tool
            
#         Returns:
#             Execution result
#         """
#         tool_name = tool_info['name']
        
#         # Create natural language prompt for Claude Code
#         param_str = ", ".join([f"{k}='{v}'" for k, v in parameters.items()])
#         prompt = f"Use the {tool_name} tool with these parameters: {param_str}"
        
#         logger.info(f"🔧 Executing tool: {tool_name}")
#         logger.info(f"   Prompt: {prompt}")
        
#         try:
#             # Execute via subprocess
#             result = await asyncio.get_event_loop().run_in_executor(
#                 None, 
#                 self._execute_claude_command, 
#                 prompt
#             )
            
#             # Parse result
#             return self._parse_tool_result(result, tool_name)
            
#         except Exception as e:
#             logger.error(f"Tool execution failed: {e}")
#             return {
#                 "success": False,
#                 "error": str(e),
#                 "tool": tool_name
#             }
    
#     def _execute_claude_command(self, prompt: str) -> str:
#         """Execute Claude command synchronously"""
#         # Write prompt to input file
#         input_file = self.claude_cwd / "tool_input.txt"
#         with open(input_file, 'w', encoding='utf-8') as f:
#             f.write(prompt)
        
#         # Execute Claude
#         proc = subprocess.Popen(
#             self.claude_cmd,
#             stdin=subprocess.PIPE,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             cwd=str(self.claude_cwd),
#             text=True,
#             encoding='utf-8'
#         )
        
#         # Feed input
#         with open(input_file, 'r', encoding='utf-8') as f:
#             input_data = f.read()
        
#         stdout, stderr = proc.communicate(input=input_data, timeout=self.timeout)
        
#         # Clean up
#         if input_file.exists():
#             input_file.unlink()
        
#         return stdout
    
#     def _parse_tool_result(self, raw_output: str, tool_name: str) -> Dict[str, Any]:
#         """Parse tool execution result from Claude output"""
#         # Basic parsing - can be enhanced based on actual output patterns
#         if "error" in raw_output.lower() or "failed" in raw_output.lower():
#             return {
#                 "success": False,
#                 "output": raw_output,
#                 "tool": tool_name
#             }
        
#         return {
#             "success": True,
#             "output": raw_output,
#             "tool": tool_name
#         }


# class DynamicAgent(BaseAgent):
#     """
#     Generic agent implementation that can handle any agent type
#     Uses the local LLM to determine actions based on role
#     """
    
#     async def execute(self, input_data: Any) -> Any:
#         """
#         Dynamic execution based on agent role and available tools
#         """
#         # Build context for LLM
#         context = {
#             "role": self.identity['role'],
#             "input": input_data,
#             "available_tools": [t['name'] for t in self.tools],
#             "position": self.position,
#             "outputs_to": self.outputs_to
#         }
        
#         # Create prompt for local LLM
#         prompt = self._build_execution_prompt(context)
        
#         # Get LLM response
#         llm_response = await self.call_local_llm(prompt)
        
#         # Parse and execute any tool calls
#         result = await self._process_llm_response(llm_response)
        
#         return result
    
#     def _build_execution_prompt(self, context: Dict[str, Any]) -> str:
#         """Build prompt for LLM based on agent context"""
#         prompt = f"""
# You are {self.agent_name} with the following role:
# {context['role']}

# Input received: {json.dumps(context['input'], indent=2) if isinstance(context['input'], dict) else context['input']}

# Available tools: {', '.join(context['available_tools'])}

# Based on your role and the input, determine what actions to take.
# If you need to use tools, respond in this format:
# TOOL_CALL: tool_name
# PARAMETERS: 
#   param1: value1
#   param2: value2

# After any tool calls, provide your final output that will be passed to the next agent.

# Remember: You are agent {context['position']} in the workflow. Your output goes to: {context['outputs_to']}
# """
#         return prompt
    
#     async def _process_llm_response(self, response: str) -> Any:
#         """Process LLM response and execute any tool calls"""
#         lines = response.split('\n')
#         final_output = []
        
#         i = 0
#         while i < len(lines):
#             line = lines[i].strip()
            
#             # Check for tool call
#             if line.startswith("TOOL_CALL:"):
#                 tool_name = line.split(":", 1)[1].strip()
#                 parameters = {}
                
#                 # Parse parameters
#                 i += 1
#                 if i < len(lines) and lines[i].strip() == "PARAMETERS:":
#                     i += 1
#                     while i < len(lines) and lines[i].strip() and not lines[i].startswith("TOOL_CALL:"):
#                         param_line = lines[i].strip()
#                         if ':' in param_line:
#                             key, value = param_line.split(':', 1)
#                             parameters[key.strip()] = value.strip()
#                         i += 1
                
#                 # Execute tool
#                 result = await self.execute_tool(tool_name, parameters)
#                 final_output.append(result)
#             else:
#                 if line and not line.startswith("PARAMETERS:"):
#                     final_output.append(line)
#                 i += 1
        
#         # Return appropriate format
#         if len(final_output) == 1:
#             return final_output[0]
#         else:
#             return '\n'.join(str(item) for item in final_output)


# class AgentFactory:
#     """
#     Factory for creating agents from BA_enhanced.json
#     """
    
#     def __init__(self, llm_url: str = "http://127.0.0.1:1234/v1/chat/completions", output_dir: str = None):
#         """
#         Initialize Agent Factory
        
#         Args:
#             llm_url: LM Studio API endpoint for Qwen 2.5 Coder 14B
#             output_dir: Directory to save generated agent files
#         """
#         self.llm_url = llm_url
#         self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "created_agents"
        
#         # Workflow context with correct model identifier
#         self.workflow_context = {
#             'llm_url': llm_url,
#             'claude_cwd': Path(r"C:\Users\manis"),
#             'shared_state': {},
#             'model_id': 'qwen2.5-coder-14b-instruct'  # Your LM Studio model identifier
#         }
    
#     def create_agent(self, agent_config: Dict[str, Any]) -> BaseAgent:
#         """
#         Create an agent instance based on configuration
        
#         Args:
#             agent_config: Agent configuration from BA_enhanced.json
            
#         Returns:
#             Instantiated agent
#         """
#         # For now, all agents use the DynamicAgent implementation
#         # In future, we could have specialized classes for certain agent types
        
#         agent = DynamicAgent(agent_config, self.workflow_context)
#         return agent
    
#     def create_agent_file(self, agent_config: Dict[str, Any], workflow_id: str) -> Path:
#         """
#         Create a standalone Python file for an individual agent
        
#         Args:
#             agent_config: Agent configuration from BA_enhanced.json
#             workflow_id: Workflow identifier for organization
            
#         Returns:
#             Path to created agent file
#         """
#         # Ensure output directory exists
#         agent_dir = self.output_dir / workflow_id
#         agent_dir.mkdir(parents=True, exist_ok=True)
        
#         # Clean agent name for filename
#         agent_name = agent_config['agent_name'].replace('*', '').replace(' ', '_').lower()
#         filename = f"{agent_config['agent_id']}_{agent_name}.py"
#         filepath = agent_dir / filename
        
#         # Generate agent code
#         agent_code = self._generate_agent_code(agent_config)
        
#         # Write to file
#         with open(filepath, 'w', encoding='utf-8') as f:
#             f.write(agent_code)
        
#         logger.info(f"📄 Created agent file: {filepath}")
#         return filepath
    
#     def _generate_agent_code(self, agent_config: Dict[str, Any]) -> str:
#         """
#         Generate standalone Python code for an agent
#         """
#         agent_name = agent_config['agent_name'].replace('*', '').strip()
#         class_name = ''.join(word.capitalize() for word in agent_name.replace('-', ' ').replace('_', ' ').split())
        
#         code = f'''#!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# {agent_name} - Auto-generated agent for MetaFlow
# Position: {agent_config['position']}
# Role: {agent_config['identity']['role']}
# """

# from pathlib import Path
# from typing import Dict, List, Any, Optional
# import json
# import logging
# import asyncio
# from datetime import datetime

# # Import base agent (this would need to be in Python path)
# # from agent_creation_factory import BaseAgent, MCPToolExecutor

# logger = logging.getLogger(__name__)


# class {class_name}:
#     """
#     {agent_config['identity']['description']}
#     """
    
#     def __init__(self):
#         # Agent Identity
#         self.agent_id = "{agent_config['agent_id']}"
#         self.agent_name = "{agent_config['agent_name']}"
#         self.position = {agent_config['position']}
        
#         # Role Definition
#         self.role = """{agent_config['identity']['role']}"""
#         self.agent_type = "{agent_config['identity']['agent_type']}"
        
#         # Tools Configuration
#         self.tools = {json.dumps(agent_config['tools'], indent=8)}
        
#         # Data Interface
#         self.input_types = {agent_config['data_interface']['input']['types']}
#         self.output_types = {agent_config['data_interface']['output']['types']}
#         self.output_delivery = "{agent_config['data_interface']['output']['delivery']}"
        
#         # LLM Configuration
#         self.llm_config = {{
#             "provider": "{agent_config['llm_config']['provider']}",
#             "model": "{agent_config['llm_config']['model']}",
#             "reasoning": "{agent_config['llm_config']['reasoning']}",
#             "temperature": {agent_config['llm_config']['params']['temperature']},
#             "max_tokens": {agent_config['llm_config']['params']['max_tokens']}
#         }}
        
#         # Dependencies and Outputs
#         self.dependencies = {agent_config['interface']['dependencies']}
#         self.outputs_to = {agent_config['interface']['outputs_to']}
#         self.error_strategy = "{agent_config['interface']['error_strategy']}"
        
#         logger.info(f"✅ Initialized {{self.agent_name}} (ID: {{self.agent_id}})")
    
#     async def execute(self, input_data: Any) -> Any:
#         """
#         Execute the agent's main task
        
#         Args:
#             input_data: Input from previous agent or initial data
            
#         Returns:
#             Processed output for next agent
#         """
#         logger.info(f"🚀 {{self.agent_name}} starting execution...")
        
#         try:
#             # Agent-specific logic based on role
#             result = await self._process_task(input_data)
            
#             logger.info(f"✅ {{self.agent_name}} completed successfully")
#             return result
            
#         except Exception as e:
#             logger.error(f"❌ {{self.agent_name}} failed: {{e}}")
#             raise
    
#     async def _process_task(self, input_data: Any) -> Any:
#         """
#         Main processing logic for {agent_name}
        
#         This method should:
#         1. Analyze the input based on the agent's role
#         2. Use LLM for reasoning if needed
#         3. Execute required tools
#         4. Format and return the output
#         """
#         # TODO: Implement specific logic based on role:
#         # {agent_config['identity']['role']}
        
#         # For now, return a placeholder
#         return {{
#             "agent": self.agent_name,
#             "status": "processed",
#             "input_received": input_data,
#             "timestamp": datetime.now().isoformat(),
#             "next_agent": self.outputs_to[0] if self.outputs_to else None
#         }}
    
#     def get_info(self) -> Dict[str, Any]:
#         """Get agent information"""
#         return {{
#             "agent_id": self.agent_id,
#             "agent_name": self.agent_name,
#             "position": self.position,
#             "role": self.role,
#             "tools": [tool["name"] for tool in self.tools],
#             "dependencies": self.dependencies,
#             "outputs_to": self.outputs_to
#         }}


# # Standalone execution for testing
# if __name__ == "__main__":
#     async def test_agent():
#         agent = {class_name}()
#         print(f"Agent Info: {{json.dumps(agent.get_info(), indent=2)}}")
        
#         # Test execution with sample input
#         test_input = {{"test": "data", "timestamp": datetime.now().isoformat()}}
#         result = await agent.execute(test_input)
#         print(f"Execution Result: {{json.dumps(result, indent=2, default=str)}}")
    
#     asyncio.run(test_agent())
# '''
        
#         return code
    
#     def create_workflow(self, ba_enhanced_path: str) -> 'WorkflowOrchestrator':
#         """
#         Create complete workflow from BA_enhanced.json
        
#         Args:
#             ba_enhanced_path: Path to BA_enhanced.json file
            
#         Returns:
#             WorkflowOrchestrator instance
#         """
#         # Load configuration
#         with open(ba_enhanced_path, 'r', encoding='utf-8') as f:
#             workflow_data = json.load(f)
        
#         workflow_id = workflow_data['workflow_metadata']['workflow_id']
        
#         # Create individual agent files
#         logger.info(f"📁 Creating agent files in: {self.output_dir / workflow_id}")
#         for agent_config in workflow_data['agents']:
#             self.create_agent_file(agent_config, workflow_id)
        
#         # Create workflow documentation
#         self._create_workflow_docs(workflow_data, workflow_id)
        
#         # Create agents for runtime
#         agents = {}
#         for agent_config in workflow_data['agents']:
#             agent = self.create_agent(agent_config)
#             agents[agent.agent_id] = agent
        
#         # Create orchestrator
#         orchestrator = WorkflowOrchestrator(
#             agents=agents,
#             workflow_metadata=workflow_data['workflow_metadata'],
#             orchestration_config=workflow_data['orchestration']
#         )
        
#         return orchestrator
    
#     def _create_workflow_docs(self, workflow_data: Dict, workflow_id: str):
#         """Create workflow documentation file"""
#         doc_path = self.output_dir / workflow_id / "workflow_documentation.md"
        
#         doc_content = f"""# Workflow Documentation: {workflow_id}

# ## Overview
# - **Domain**: {workflow_data['workflow_metadata']['domain']}
# - **Architecture**: {workflow_data['workflow_metadata']['selected_architecture']}
# - **Total Agents**: {workflow_data['workflow_metadata']['total_agents']}
# - **Estimated Execution Time**: {workflow_data['workflow_metadata']['estimated_execution_time']}

# ## Agent Pipeline

# """
#         for agent in workflow_data['agents']:
#             doc_content += f"""### {agent['position']}. {agent['agent_name']}
# - **ID**: {agent['agent_id']}
# - **Role**: {agent['identity']['role']}
# - **Tools**: {', '.join([t['name'] for t in agent['tools']])}
# - **Dependencies**: {', '.join(agent['interface']['dependencies']) or 'None'}
# - **Outputs To**: {', '.join(agent['interface']['outputs_to']) or 'None'}

# """
        
#         doc_content += f"""## Orchestration Pattern
# - **Type**: {workflow_data['orchestration']['pattern']}
# - **Connections**: {len(workflow_data['orchestration']['connections'])} connections

# ## Usage
# ```python
# from agent_creation_factory import AgentFactory

# factory = AgentFactory()
# workflow = factory.create_workflow("{workflow_id}/BA_enhanced.json")
# result = await workflow.execute(initial_input)
# ```
# """
        
#         with open(doc_path, 'w', encoding='utf-8') as f:
#             f.write(doc_content)
        
#         logger.info(f"📝 Created workflow documentation: {doc_path}")


# class WorkflowOrchestrator:
#     """
#     Manages workflow execution based on selected architecture pattern
#     """
    
#     def __init__(self, agents: Dict[str, BaseAgent], workflow_metadata: Dict, orchestration_config: Dict):
#         self.agents = agents
#         self.metadata = workflow_metadata
#         self.orchestration = orchestration_config
#         self.pattern = orchestration_config['pattern']
#         self.connections = orchestration_config['connections']
        
#         # State tracking
#         self.agent_states = {
#             agent_id: AgentState(agent_id=agent_id, status='ready')
#             for agent_id in agents.keys()
#         }
        
#         logger.info(f"📊 Workflow Orchestrator initialized")
#         logger.info(f"   Pattern: {self.pattern}")
#         logger.info(f"   Total agents: {len(self.agents)}")
    
#     async def execute(self, initial_input: Any = None) -> Dict[str, Any]:
#         """
#         Execute the workflow based on the orchestration pattern
        
#         Note: The workflow specification in BA_enhanced.json already contains
#         all necessary context from the user's original prompt. The agents
#         will work based on their defined roles and the workflow structure.
        
#         Args:
#             initial_input: Optional initial data for the first agent.
#                          If not provided, agents will work based on their roles.
#         """
#         logger.info(f"🎯 Starting workflow execution: {self.metadata['workflow_id']}")
#         logger.info(f"   Architecture: {self.metadata['selected_architecture']}")
#         logger.info(f"   Domain: {self.metadata['domain']}")
        
#         # If no initial input provided, create a minimal context
#         if initial_input is None:
#             initial_input = {
#                 "workflow_id": self.metadata['workflow_id'],
#                 "execution_start": datetime.now().isoformat(),
#                 "note": "Agents will execute based on their predefined roles from BA_enhanced.json"
#             }
        
#         start_time = datetime.now()
        
#         try:
#             if "pipeline" in self.pattern.lower() or "sequential" in self.pattern.lower():
#                 result = await self._execute_pipeline(initial_input)
#             elif "event" in self.pattern.lower():
#                 result = await self._execute_event_driven(initial_input)
#             elif "hub" in self.pattern.lower():
#                 result = await self._execute_hub_spoke(initial_input)
#             elif "hierarchical" in self.pattern.lower():
#                 result = await self._execute_hierarchical(initial_input)
#             elif "collaborative" in self.pattern.lower():
#                 result = await self._execute_collaborative(initial_input)
#             else:
#                 # Default to pipeline
#                 result = await self._execute_pipeline(initial_input)
            
#             end_time = datetime.now()
#             duration = (end_time - start_time).total_seconds()
            
#             logger.info(f"✅ Workflow completed in {duration:.2f} seconds")
            
#             return {
#                 "success": True,
#                 "workflow_id": self.metadata['workflow_id'],
#                 "duration": duration,
#                 "result": result,
#                 "agent_states": self._get_states_summary()
#             }
            
#         except Exception as e:
#             logger.error(f"❌ Workflow failed: {e}")
#             return {
#                 "success": False,
#                 "workflow_id": self.metadata['workflow_id'],
#                 "error": str(e),
#                 "agent_states": self._get_states_summary()
#             }
    
#     async def _execute_pipeline(self, initial_input: Any) -> Any:
#         """Execute agents in sequential pipeline"""
#         current_input = initial_input
        
#         # Get agents sorted by position
#         sorted_agents = sorted(self.agents.values(), key=lambda a: a.position)
        
#         for agent in sorted_agents:
#             logger.info(f"🔄 Executing agent {agent.position}: {agent.agent_name}")
            
#             # Run agent
#             state = await agent.run(current_input)
#             self.agent_states[agent.agent_id] = state
            
#             if state.status == 'failed':
#                 raise Exception(f"Agent {agent.agent_name} failed: {state.error}")
            
#             # Pass output to next agent
#             current_input = state.output_data
        
#         return current_input
    
#     async def _execute_event_driven(self, initial_input: Any) -> Any:
#         """Execute event-driven architecture"""
#         # TODO: Implement event-driven execution
#         # For now, fall back to pipeline
#         logger.warning("Event-driven execution not yet implemented, using pipeline")
#         return await self._execute_pipeline(initial_input)
    
#     async def _execute_hub_spoke(self, initial_input: Any) -> Any:
#         """Execute hub-and-spoke architecture"""
#         # TODO: Implement hub-spoke execution
#         # For now, fall back to pipeline
#         logger.warning("Hub-spoke execution not yet implemented, using pipeline")
#         return await self._execute_pipeline(initial_input)
    
#     async def _execute_hierarchical(self, initial_input: Any) -> Any:
#         """Execute hierarchical architecture"""
#         # TODO: Implement hierarchical execution
#         # For now, fall back to pipeline
#         logger.warning("Hierarchical execution not yet implemented, using pipeline")
#         return await self._execute_pipeline(initial_input)
    
#     async def _execute_collaborative(self, initial_input: Any) -> Any:
#         """Execute collaborative architecture"""
#         # TODO: Implement collaborative execution
#         # For now, fall back to pipeline
#         logger.warning("Collaborative execution not yet implemented, using pipeline")
#         return await self._execute_pipeline(initial_input)
    
#     def _get_states_summary(self) -> Dict[str, Dict]:
#         """Get summary of all agent states"""
#         summary = {}
#         for agent_id, state in self.agent_states.items():
#             summary[agent_id] = {
#                 "status": state.status,
#                 "error": state.error,
#                 "duration": (state.end_time - state.start_time).total_seconds() if state.end_time and state.start_time else None
#             }
#         return summary


# # Example usage
# async def main():
#     """
#     Agent Factory - Creates agents from BA_enhanced.json
    
#     The workflow is:
#     1. User Prompt → Base Agent (Qwen 2.5 14B) → BA_op.json
#     2. BA_op.json → Tool Mapper → BA_enhanced.json
#     3. BA_enhanced.json → Agent Factory → Created Agents
    
#     This factory only needs BA_enhanced.json as input.
#     """
#     import sys
    
#     if len(sys.argv) < 2:
#         print("Usage: python agent_creation_factory.py <path_to_BA_enhanced.json>")
#         print("\nThis factory creates agents from the enhanced workflow specification.")
#         print("The user prompt has already been processed by Base Agent and Tool Mapper.")
#         sys.exit(1)
    
#     ba_enhanced_path = sys.argv[1]
    
#     print(f"\n🏭 MetaFlow Agent Factory")
#     print(f"="*60)
#     print(f"📄 Input: {ba_enhanced_path}")
#     print(f"🤖 LLM: Qwen 2.5 14B (local)")
#     print(f"="*60)
    
#     # Initialize factory
#     factory = AgentFactory()
    
#     # Create workflow from BA_enhanced.json
#     print("\n⚙️  Creating workflow and agents...")
#     workflow = factory.create_workflow(ba_enhanced_path)
    
#     print(f"\n✅ Workflow created successfully!")
#     print(f"📁 Agent files saved to: {factory.output_dir}")
    
#     # The workflow is now ready to execute
#     # In production, this would be triggered by external events or scheduler
#     print("\n🎯 Workflow is ready for execution")
#     print("Agents will process tasks according to the workflow specification")
    
#     # Optional: Show workflow summary
#     with open(ba_enhanced_path, 'r') as f:
#         data = json.load(f)
    
#     print(f"\n📊 Workflow Summary:")
#     print(f"   - Workflow ID: {data['workflow_metadata']['workflow_id']}")
#     print(f"   - Domain: {data['workflow_metadata']['domain']}")
#     print(f"   - Architecture: {data['workflow_metadata']['selected_architecture']}")
#     print(f"   - Total Agents: {data['workflow_metadata']['total_agents']}")
#     print(f"   - Orchestration: {data['orchestration']['pattern']}")


# if __name__ == "__main__":
#     # Run factory
#     asyncio.run(main())



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Creation Factory for MetaFlow Platform
Creates and manages LangChain agents based on BA_enhanced.json specifications

IMPORTANT: Two-phase operation:
1. GENERATION PHASE (No LLM needed): Creates Python files from BA_enhanced.json templates
2. EXECUTION PHASE (Requires LLM): Agents use Qwen 2.5 14B for reasoning during runtime

The factory can generate agent files without LM Studio running, but agents 
need LM Studio running when they actually execute tasks.
"""

import json
import subprocess
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class AgentMessage:
    """Message structure for inter-agent communication"""
    sender_id: str
    receiver_id: str
    message_type: str  # 'data', 'status', 'error', 'request'
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)
    requires_response: bool = False


@dataclass
class AgentState:
    """Shared state for agent execution"""
    agent_id: str
    status: str  # 'ready', 'running', 'completed', 'failed', 'waiting'
    input_data: Any = None
    output_data: Any = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    dependencies_met: bool = False


class BaseAgent(ABC):
    """
    Universal template for all MetaFlow agents
    Handles common functionality while allowing specific implementations
    """
    
    def __init__(self, agent_config: Dict[str, Any], workflow_context: Dict[str, Any]):
        """
        Initialize base agent with configuration from BA_enhanced.json
        
        Args:
            agent_config: Individual agent configuration from JSON
            workflow_context: Overall workflow metadata and shared resources
        """
        # 1. Agent Identity
        self.agent_id = agent_config['agent_id']
        self.agent_name = agent_config['agent_name']
        self.position = agent_config['position']
        self.identity = agent_config['identity']
        
        # 2. MCP Tool Access
        self.tools = agent_config.get('tools', [])
        self.mcp_executor = MCPToolExecutor(workflow_context.get('claude_cwd', Path(r"C:\Users\manis")))
        
        # 3. Input Processing
        self.data_interface = agent_config['data_interface']
        self.input_types = self.data_interface['input']['types']
        self.output_types = self.data_interface['output']['types']
        
        # 4. Output Formatting
        self.output_delivery = self.data_interface['output']['delivery']
        
        # 5. State Management
        self.state_config = agent_config['state']
        self.local_state = {}
        self.workflow_state = workflow_context.get('shared_state', {})
        
        # 6. Communication Interface
        self.interface_config = agent_config['interface']
        self.dependencies = self.interface_config['dependencies']
        self.outputs_to = self.interface_config['outputs_to']
        self.error_strategy = self.interface_config['error_strategy']
        self.message_queue = asyncio.Queue()
        
        # LLM Configuration
        self.llm_config = agent_config['llm_config']
        self.reasoning_type = self.llm_config['reasoning']  # 'function-calling' or 'ReAct'
        
        # Initialize local LLM connection
        self.local_llm_url = workflow_context.get('llm_url', "http://localhost:1234/v1/chat/completions")
        
        logger.info(f"✅ Initialized {self.agent_name} (ID: {self.agent_id})")
        logger.info(f"   Tools: {[t['name'] for t in self.tools]}")
        logger.info(f"   Dependencies: {self.dependencies}")
    
    @abstractmethod
    async def execute(self, input_data: Any) -> Any:
        """
        Main execution method - must be implemented by each specific agent
        
        Args:
            input_data: Input from previous agent or initial data
            
        Returns:
            Processed output for next agent
        """
        pass
    
    async def run(self, input_data: Any = None) -> AgentState:
        """
        Wrapper method that handles common execution logic
        """
        logger.info(f"🚀 {self.agent_name} starting execution...")
        
        # Initialize state
        state = AgentState(
            agent_id=self.agent_id,
            status='running',
            input_data=input_data,
            start_time=datetime.now()
        )
        
        try:
            # Validate input
            if not self._validate_input(input_data):
                raise ValueError(f"Invalid input type for {self.agent_name}")
            
            # Execute agent-specific logic
            output = await self.execute(input_data)
            
            # Format output
            formatted_output = self._format_output(output)
            
            # Update state
            state.output_data = formatted_output
            state.status = 'completed'
            state.end_time = datetime.now()
            
            logger.info(f"✅ {self.agent_name} completed successfully")
            
        except Exception as e:
            state.status = 'failed'
            state.error = str(e)
            state.end_time = datetime.now()
            
            logger.error(f"❌ {self.agent_name} failed: {e}")
            
            # Handle error based on strategy
            if self.error_strategy == 'retry':
                logger.info(f"🔄 Retrying {self.agent_name}...")
                # Implement retry logic here
            
        return state
    
    def _validate_input(self, input_data: Any) -> bool:
        """Validate input data against expected types"""
        if input_data is None:
            return 'null' in self.input_types or not self.input_types
        
        if isinstance(input_data, dict) and 'json' in self.input_types:
            return True
        if isinstance(input_data, str) and 'text' in self.input_types:
            return True
        
        return False
    
    def _format_output(self, output: Any) -> Any:
        """Format output according to interface requirements"""
        if 'json' in self.output_types and isinstance(output, str):
            try:
                return json.loads(output)
            except:
                return {"text": output}
        
        return output
    
    async def call_local_llm(self, prompt: str) -> str:
        """
        Call local LLM (Qwen 2.5 14B) for reasoning
        
        This is where agents use the local Qwen model for decision-making,
        while Claude Code is only used for tool execution to minimize tokens.
        """
        try:
            # Prepare messages based on reasoning type
            if self.reasoning_type == 'function-calling':
                messages = [
                    {"role": "system", "content": f"You are {self.agent_name}. {self.identity['role']}"},
                    {"role": "user", "content": prompt}
                ]
            else:  # ReAct
                messages = [
                    {"role": "system", "content": f"You are {self.agent_name}. {self.identity['role']} Use the ReAct pattern: Thought, Action, Observation, Result."},
                    {"role": "user", "content": prompt}
                ]
            
            response = requests.post(
                self.local_llm_url,
                json={
                    "model": self.llm_config['model'],  # qwen2.5-coder-14b-instruct
                    "messages": messages,
                    "temperature": self.llm_config['params']['temperature'],
                    "max_tokens": self.llm_config['params']['max_tokens']
                },
                timeout=300
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                raise Exception(f"LLM call failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to call local LLM: {e}")
            raise
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an MCP tool via Claude Code
        """
        # Find the full tool info
        tool_info = next((t for t in self.tools if t['name'] == tool_name), None)
        if not tool_info:
            raise ValueError(f"Tool {tool_name} not found in agent's tool list")
        
        return await self.mcp_executor.execute_tool(tool_info, parameters)
    
    async def send_message(self, receiver_id: str, message_type: str, content: Any):
        """Send message to another agent"""
        message = AgentMessage(
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content
        )
        # In real implementation, this would use a message broker
        logger.info(f"📧 {self.agent_name} -> {receiver_id}: {message_type}")
        
    def update_shared_state(self, key: str, value: Any):
        """Update shared workflow state"""
        self.workflow_state[key] = value
        logger.info(f"📝 {self.agent_name} updated shared state: {key}")


class MCPToolExecutor:
    """
    Handles execution of MCP tools via Claude Code
    """
    
    def __init__(self, claude_cwd: Path):
        self.claude_cwd = claude_cwd
        self.claude_cmd = [
            "powershell.exe",
            "-NoLogo",
            "-NoProfile",
            "-Command",
            "claude"
        ]
        self.timeout = 300
    
    async def execute_tool(self, tool_info: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute MCP tool by generating natural language prompt for Claude
        
        Args:
            tool_info: Tool information including name and server
            parameters: Parameters to pass to the tool
            
        Returns:
            Execution result
        """
        tool_name = tool_info['name']
        
        # Create natural language prompt for Claude Code
        param_str = ", ".join([f"{k}='{v}'" for k, v in parameters.items()])
        prompt = f"Use the {tool_name} tool with these parameters: {param_str}"
        
        logger.info(f"🔧 Executing tool: {tool_name}")
        logger.info(f"   Prompt: {prompt}")
        
        try:
            # Execute via subprocess
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                self._execute_claude_command, 
                prompt
            )
            
            # Parse result
            return self._parse_tool_result(result, tool_name)
            
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }
    
    def _execute_claude_command(self, prompt: str) -> str:
        """Execute Claude command synchronously"""
        # Write prompt to input file
        input_file = self.claude_cwd / "tool_input.txt"
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        # Execute Claude
        proc = subprocess.Popen(
            self.claude_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(self.claude_cwd),
            text=True,
            encoding='utf-8'
        )
        
        # Feed input
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = f.read()
        
        stdout, stderr = proc.communicate(input=input_data, timeout=self.timeout)
        
        # Clean up
        if input_file.exists():
            input_file.unlink()
        
        return stdout
    
    def _parse_tool_result(self, raw_output: str, tool_name: str) -> Dict[str, Any]:
        """Parse tool execution result from Claude output"""
        # Basic parsing - can be enhanced based on actual output patterns
        if "error" in raw_output.lower() or "failed" in raw_output.lower():
            return {
                "success": False,
                "output": raw_output,
                "tool": tool_name
            }
        
        return {
            "success": True,
            "output": raw_output,
            "tool": tool_name
        }


class DynamicAgent(BaseAgent):
    """
    Generic agent implementation that can handle any agent type
    Uses the local LLM to determine actions based on role
    """
    
    async def execute(self, input_data: Any) -> Any:
        """
        Dynamic execution based on agent role and available tools
        """
        # Build context for LLM
        context = {
            "role": self.identity['role'],
            "input": input_data,
            "available_tools": [t['name'] for t in self.tools],
            "position": self.position,
            "outputs_to": self.outputs_to
        }
        
        # Create prompt for local LLM
        prompt = self._build_execution_prompt(context)
        
        # Get LLM response
        llm_response = await self.call_local_llm(prompt)
        
        # Parse and execute any tool calls
        result = await self._process_llm_response(llm_response)
        
        return result
    
    def _build_execution_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for LLM based on agent context"""
        prompt = f"""
You are {self.agent_name} with the following role:
{context['role']}

Input received: {json.dumps(context['input'], indent=2) if isinstance(context['input'], dict) else context['input']}

Available tools: {', '.join(context['available_tools'])}

Based on your role and the input, determine what actions to take.
If you need to use tools, respond in this format:
TOOL_CALL: tool_name
PARAMETERS: 
  param1: value1
  param2: value2

After any tool calls, provide your final output that will be passed to the next agent.

Remember: You are agent {context['position']} in the workflow. Your output goes to: {context['outputs_to']}
"""
        return prompt
    
    async def _process_llm_response(self, response: str) -> Any:
        """Process LLM response and execute any tool calls"""
        lines = response.split('\n')
        final_output = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for tool call
            if line.startswith("TOOL_CALL:"):
                tool_name = line.split(":", 1)[1].strip()
                parameters = {}
                
                # Parse parameters
                i += 1
                if i < len(lines) and lines[i].strip() == "PARAMETERS:":
                    i += 1
                    while i < len(lines) and lines[i].strip() and not lines[i].startswith("TOOL_CALL:"):
                        param_line = lines[i].strip()
                        if ':' in param_line:
                            key, value = param_line.split(':', 1)
                            parameters[key.strip()] = value.strip()
                        i += 1
                
                # Execute tool
                result = await self.execute_tool(tool_name, parameters)
                final_output.append(result)
            else:
                if line and not line.startswith("PARAMETERS:"):
                    final_output.append(line)
                i += 1
        
        # Return appropriate format
        if len(final_output) == 1:
            return final_output[0]
        else:
            return '\n'.join(str(item) for item in final_output)


class AgentFactory:
    """
    Factory for creating agents from BA_enhanced.json
    """
    
    def __init__(self, llm_url: str = "http://127.0.0.1:1234/v1/chat/completions", output_dir: str = None):
        """
        Initialize Agent Factory
        
        Args:
            llm_url: LM Studio API endpoint for Qwen 2.5 Coder 14B
            output_dir: Directory to save generated agent files
        """
        self.llm_url = llm_url
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "created_agents"
        
        # Workflow context with correct model identifier
        self.workflow_context = {
            'llm_url': llm_url,
            'claude_cwd': Path(r"C:\Users\manis"),
            'shared_state': {},
            'model_id': 'qwen2.5-coder-14b-instruct'  # Your LM Studio model identifier
        }
    
    def create_agent(self, agent_config: Dict[str, Any]) -> BaseAgent:
        """
        Create an agent instance based on configuration
        
        Args:
            agent_config: Agent configuration from BA_enhanced.json
            
        Returns:
            Instantiated agent
        """
        # For now, all agents use the DynamicAgent implementation
        # In future, we could have specialized classes for certain agent types
        
        agent = DynamicAgent(agent_config, self.workflow_context)
        return agent
    
    def create_agent_file(self, agent_config: Dict[str, Any], workflow_id: str) -> Path:
        """
        Create a standalone Python file for an individual agent
        
        Args:
            agent_config: Agent configuration from BA_enhanced.json
            workflow_id: Workflow identifier for organization
            
        Returns:
            Path to created agent file
        """
        # Ensure output directory exists
        agent_dir = self.output_dir / workflow_id
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        # Clean agent name for filename
        agent_name = agent_config['agent_name'].replace('*', '').replace(' ', '_').lower()
        filename = f"{agent_config['agent_id']}_{agent_name}.py"
        filepath = agent_dir / filename
        
        # Generate agent code
        agent_code = self._generate_agent_code(agent_config)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(agent_code)
        
        logger.info(f"📄 Created agent file: {filepath}")
        return filepath
    
    def _generate_agent_code(self, agent_config: Dict[str, Any]) -> str:
        """
        Generate standalone Python code for an agent
        """
        agent_name = agent_config['agent_name'].replace('*', '').strip()
        class_name = ''.join(word.capitalize() for word in agent_name.replace('-', ' ').replace('_', ' ').split())
        
        code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{agent_name} - Auto-generated agent for MetaFlow
Position: {agent_config['position']}
Role: {agent_config['identity']['role']}
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import logging
import asyncio
from datetime import datetime

# Import base agent (this would need to be in Python path)
# from agent_creation_factory import BaseAgent, MCPToolExecutor

logger = logging.getLogger(__name__)


class {class_name}:
    """
    {agent_config['identity']['description']}
    """
    
    def __init__(self):
        # Agent Identity
        self.agent_id = "{agent_config['agent_id']}"
        self.agent_name = "{agent_config['agent_name']}"
        self.position = {agent_config['position']}
        
        # Role Definition
        self.role = """{agent_config['identity']['role']}"""
        self.agent_type = "{agent_config['identity']['agent_type']}"
        
        # Tools Configuration
        self.tools = {json.dumps(agent_config['tools'], indent=8)}
        
        # Data Interface
        self.input_types = {agent_config['data_interface']['input']['types']}
        self.output_types = {agent_config['data_interface']['output']['types']}
        self.output_delivery = "{agent_config['data_interface']['output']['delivery']}"
        
        # LLM Configuration
        self.llm_config = {{
            "provider": "{agent_config['llm_config']['provider']}",
            "model": "{agent_config['llm_config']['model']}",
            "reasoning": "{agent_config['llm_config']['reasoning']}",
            "temperature": {agent_config['llm_config']['params']['temperature']},
            "max_tokens": {agent_config['llm_config']['params']['max_tokens']}
        }}
        
        # Dependencies and Outputs
        self.dependencies = {agent_config['interface']['dependencies']}
        self.outputs_to = {agent_config['interface']['outputs_to']}
        self.error_strategy = "{agent_config['interface']['error_strategy']}"
        
        logger.info(f"✅ Initialized {{self.agent_name}} (ID: {{self.agent_id}})")
    
    async def execute(self, input_data: Any) -> Any:
        """
        Execute the agent's main task
        
        Args:
            input_data: Input from previous agent or initial data
            
        Returns:
            Processed output for next agent
        """
        logger.info(f"🚀 {{self.agent_name}} starting execution...")
        
        try:
            # Agent-specific logic based on role
            result = await self._process_task(input_data)
            
            logger.info(f"✅ {{self.agent_name}} completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ {{self.agent_name}} failed: {{e}}")
            raise
    
    async def _process_task(self, input_data: Any) -> Any:
        """
        Main processing logic for {agent_name}
        
        This method should:
        1. Analyze the input based on the agent's role
        2. Use LLM for reasoning if needed
        3. Execute required tools
        4. Format and return the output
        """
        # TODO: Implement specific logic based on role:
        # {agent_config['identity']['role']}
        
        # For now, return a placeholder
        return {{
            "agent": self.agent_name,
            "status": "processed",
            "input_received": input_data,
            "timestamp": datetime.now().isoformat(),
            "next_agent": self.outputs_to[0] if self.outputs_to else None
        }}
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {{
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "position": self.position,
            "role": self.role,
            "tools": [tool["name"] for tool in self.tools],
            "dependencies": self.dependencies,
            "outputs_to": self.outputs_to
        }}


# Standalone execution for testing
if __name__ == "__main__":
    async def test_agent():
        agent = {class_name}()
        print(f"Agent Info: {{json.dumps(agent.get_info(), indent=2)}}")
        
        # Test execution with sample input
        test_input = {{"test": "data", "timestamp": datetime.now().isoformat()}}
        result = await agent.execute(test_input)
        print(f"Execution Result: {{json.dumps(result, indent=2, default=str)}}")
    
    asyncio.run(test_agent())
'''
        
        return code
    
    def create_workflow(self, ba_enhanced_path: str) -> 'WorkflowOrchestrator':
        """
        Create complete workflow from BA_enhanced.json
        
        Args:
            ba_enhanced_path: Path to BA_enhanced.json file
            
        Returns:
            WorkflowOrchestrator instance
        """
        # Load configuration
        with open(ba_enhanced_path, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        
        workflow_id = workflow_data['workflow_metadata']['workflow_id']
        
        # Create individual agent files
        logger.info(f"📁 Creating agent files in: {self.output_dir / workflow_id}")
        for agent_config in workflow_data['agents']:
            self.create_agent_file(agent_config, workflow_id)
        
        # Create workflow documentation
        self._create_workflow_docs(workflow_data, workflow_id)
        
        # Create agents for runtime
        agents = {}
        for agent_config in workflow_data['agents']:
            agent = self.create_agent(agent_config)
            agents[agent.agent_id] = agent
        
        # Create orchestrator
        orchestrator = WorkflowOrchestrator(
            agents=agents,
            workflow_metadata=workflow_data['workflow_metadata'],
            orchestration_config=workflow_data['orchestration']
        )
        
        return orchestrator
    
    def _create_workflow_docs(self, workflow_data: Dict, workflow_id: str):
        """Create workflow documentation file"""
        doc_path = self.output_dir / workflow_id / "workflow_documentation.md"
        
        doc_content = f"""# Workflow Documentation: {workflow_id}

## Overview
- **Domain**: {workflow_data['workflow_metadata']['domain']}
- **Architecture**: {workflow_data['workflow_metadata']['selected_architecture']}
- **Total Agents**: {workflow_data['workflow_metadata']['total_agents']}
- **Estimated Execution Time**: {workflow_data['workflow_metadata']['estimated_execution_time']}

## Agent Pipeline

"""
        for agent in workflow_data['agents']:
            doc_content += f"""### {agent['position']}. {agent['agent_name']}
- **ID**: {agent['agent_id']}
- **Role**: {agent['identity']['role']}
- **Tools**: {', '.join([t['name'] for t in agent['tools']])}
- **Dependencies**: {', '.join(agent['interface']['dependencies']) or 'None'}
- **Outputs To**: {', '.join(agent['interface']['outputs_to']) or 'None'}

"""
        
        doc_content += f"""## Orchestration Pattern
- **Type**: {workflow_data['orchestration']['pattern']}
- **Connections**: {len(workflow_data['orchestration']['connections'])} connections

## Usage
```python
from agent_creation_factory import AgentFactory

factory = AgentFactory()
workflow = factory.create_workflow("{workflow_id}/BA_enhanced.json")
result = await workflow.execute(initial_input)
```
"""
        
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        logger.info(f"📝 Created workflow documentation: {doc_path}")


class WorkflowOrchestrator:
    """
    Manages workflow execution based on selected architecture pattern
    """
    
    def __init__(self, agents: Dict[str, BaseAgent], workflow_metadata: Dict, orchestration_config: Dict):
        self.agents = agents
        self.metadata = workflow_metadata
        self.orchestration = orchestration_config
        self.pattern = orchestration_config['pattern']
        self.connections = orchestration_config['connections']
        
        # State tracking
        self.agent_states = {
            agent_id: AgentState(agent_id=agent_id, status='ready')
            for agent_id in agents.keys()
        }
        
        logger.info(f"📊 Workflow Orchestrator initialized")
        logger.info(f"   Pattern: {self.pattern}")
        logger.info(f"   Total agents: {len(self.agents)}")
    
    async def execute(self, initial_input: Any = None) -> Dict[str, Any]:
        """
        Execute the workflow based on the orchestration pattern
        
        Note: The workflow specification in BA_enhanced.json already contains
        all necessary context from the user's original prompt. The agents
        will work based on their defined roles and the workflow structure.
        
        Args:
            initial_input: Optional initial data for the first agent.
                         If not provided, agents will work based on their roles.
        """
        logger.info(f"🎯 Starting workflow execution: {self.metadata['workflow_id']}")
        logger.info(f"   Architecture: {self.metadata['selected_architecture']}")
        logger.info(f"   Domain: {self.metadata['domain']}")
        
        # If no initial input provided, create a minimal context
        if initial_input is None:
            initial_input = {
                "workflow_id": self.metadata['workflow_id'],
                "execution_start": datetime.now().isoformat(),
                "note": "Agents will execute based on their predefined roles from BA_enhanced.json"
            }
        
        start_time = datetime.now()
        
        try:
            if "pipeline" in self.pattern.lower() or "sequential" in self.pattern.lower():
                result = await self._execute_pipeline(initial_input)
            elif "event" in self.pattern.lower():
                result = await self._execute_event_driven(initial_input)
            elif "hub" in self.pattern.lower():
                result = await self._execute_hub_spoke(initial_input)
            elif "hierarchical" in self.pattern.lower():
                result = await self._execute_hierarchical(initial_input)
            elif "collaborative" in self.pattern.lower():
                result = await self._execute_collaborative(initial_input)
            else:
                # Default to pipeline
                result = await self._execute_pipeline(initial_input)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"✅ Workflow completed in {duration:.2f} seconds")
            
            return {
                "success": True,
                "workflow_id": self.metadata['workflow_id'],
                "duration": duration,
                "result": result,
                "agent_states": self._get_states_summary()
            }
            
        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}")
            return {
                "success": False,
                "workflow_id": self.metadata['workflow_id'],
                "error": str(e),
                "agent_states": self._get_states_summary()
            }
    
    async def _execute_pipeline(self, initial_input: Any) -> Any:
        """Execute agents in sequential pipeline"""
        current_input = initial_input
        
        # Get agents sorted by position
        sorted_agents = sorted(self.agents.values(), key=lambda a: a.position)
        
        for agent in sorted_agents:
            logger.info(f"🔄 Executing agent {agent.position}: {agent.agent_name}")
            
            # Run agent
            state = await agent.run(current_input)
            self.agent_states[agent.agent_id] = state
            
            if state.status == 'failed':
                raise Exception(f"Agent {agent.agent_name} failed: {state.error}")
            
            # Pass output to next agent
            current_input = state.output_data
        
        return current_input
    
    async def _execute_event_driven(self, initial_input: Any) -> Any:
        """Execute event-driven architecture"""
        # TODO: Implement event-driven execution
        # For now, fall back to pipeline
        logger.warning("Event-driven execution not yet implemented, using pipeline")
        return await self._execute_pipeline(initial_input)
    
    async def _execute_hub_spoke(self, initial_input: Any) -> Any:
        """Execute hub-and-spoke architecture"""
        # TODO: Implement hub-spoke execution
        # For now, fall back to pipeline
        logger.warning("Hub-spoke execution not yet implemented, using pipeline")
        return await self._execute_pipeline(initial_input)
    
    async def _execute_hierarchical(self, initial_input: Any) -> Any:
        """Execute hierarchical architecture"""
        # TODO: Implement hierarchical execution
        # For now, fall back to pipeline
        logger.warning("Hierarchical execution not yet implemented, using pipeline")
        return await self._execute_pipeline(initial_input)
    
    async def _execute_collaborative(self, initial_input: Any) -> Any:
        """Execute collaborative architecture"""
        # TODO: Implement collaborative execution
        # For now, fall back to pipeline
        logger.warning("Collaborative execution not yet implemented, using pipeline")
        return await self._execute_pipeline(initial_input)
    
    def _get_states_summary(self) -> Dict[str, Dict]:
        """Get summary of all agent states"""
        summary = {}
        for agent_id, state in self.agent_states.items():
            summary[agent_id] = {
                "status": state.status,
                "error": state.error,
                "duration": (state.end_time - state.start_time).total_seconds() if state.end_time and state.start_time else None
            }
        return summary


# Example usage
async def main():
    """
    Agent Factory - Creates agents from BA_enhanced.json
    
    The workflow is:
    1. User Prompt → Base Agent (Qwen 2.5 14B) → BA_op.json
    2. BA_op.json → Tool Mapper → BA_enhanced.json
    3. BA_enhanced.json → Agent Factory → Created Agents
    
    This factory only needs BA_enhanced.json as input.
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python agent_creation_factory.py <path_to_BA_enhanced.json>")
        print("\nThis factory creates agents from the enhanced workflow specification.")
        print("The user prompt has already been processed by Base Agent and Tool Mapper.")
        sys.exit(1)
    
    ba_enhanced_path = sys.argv[1]
    
    print(f"\n🏭 MetaFlow Agent Factory")
    print(f"="*60)
    print(f"📄 Input: {ba_enhanced_path}")
    print(f"🤖 LLM: Qwen 2.5 14B (local)")
    print(f"="*60)
    
    # Initialize factory
    factory = AgentFactory()
    
    # Create workflow from BA_enhanced.json
    print("\n⚙️  Creating workflow and agents...")
    workflow = factory.create_workflow(ba_enhanced_path)
    
    print(f"\n✅ Workflow created successfully!")
    print(f"📁 Agent files saved to: {factory.output_dir}")
    
    # The workflow is now ready to execute
    # In production, this would be triggered by external events or scheduler
    print("\n🎯 Workflow is ready for execution")
    print("Agents will process tasks according to the workflow specification")
    
    # Optional: Show workflow summary
    with open(ba_enhanced_path, 'r') as f:
        data = json.load(f)
    
    print(f"\n📊 Workflow Summary:")
    print(f"   - Workflow ID: {data['workflow_metadata']['workflow_id']}")
    print(f"   - Domain: {data['workflow_metadata']['domain']}")
    print(f"   - Architecture: {data['workflow_metadata']['selected_architecture']}")
    print(f"   - Total Agents: {data['workflow_metadata']['total_agents']}")
    print(f"   - Orchestration: {data['orchestration']['pattern']}")


if __name__ == "__main__":
    # Run factory
    asyncio.run(main())