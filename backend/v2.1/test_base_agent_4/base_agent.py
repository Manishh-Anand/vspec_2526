# import sys
# import requests
# import importlib.util
# from pathlib import Path


# class BaseAgent:
#     def __init__(self, input_file, output_file, api_url="http://localhost:11434/api/generate"):
#         self.input_file = input_file
#         self.output_file = output_file
#         self.api_url = api_url
#         self.prompt_content = None

#         self.system_prompt = """

# You are a Base Agent in an agentic system. Your role is to:

# 1. Read and understand the user prompt/task
# 2. Maintain context throughout workflow analysis
# 3. Analyze tasks and determine which MCP tools need to be called
# 4. Manage workflow execution and coordinate tool usage
# 5. Handle error recovery and fallback strategies
# 6. Select the most appropriate multi-agent architecture for the task
# 7. Based on the user prompt, list out the sub-agents sequentially to fulfill the task
# 8. List the tools that need to be created
# 9. Explain how the sub-agents will use the tools to complete the work

# ## Multi-Agent Architecture Options

# You must select ONE of these 5 architectures based on the task requirements:

# **1. Pipeline/Sequential**
# - Use for: Linear workflows, step-by-step processes, data transformation chains
# - Best when: Tasks have clear sequential dependencies (A → B → C)
# - Examples: Content creation workflows, data processing pipelines, approval chains

# **2. Event-Driven** 
# - Use for: Reactive workflows, monitoring systems, trigger-based automation
# - Best when: Tasks need to respond to events or conditions ("when X happens, do Y")
# - Examples: Alert systems, conditional workflows, real-time monitoring

# **3. Hierarchical**
# - Use for: Complex tasks needing supervision, multi-level approval, task delegation
# - Best when: Clear authority structure needed, quality control at multiple levels
# - Examples: Project management, escalation workflows, multi-tier processing

# **4. Hub and Spoke**
# - Use for: Centralized coordination, task distribution, specialist management
# - Best when: One coordinator needs to manage multiple specialist agents
# - Examples: Customer service routing, resource allocation, centralized orchestration

# **5. Collaborative**
# - Use for: Peer-to-peer cooperation, multi-perspective analysis, consensus building
# - Best when: Agents need to work together as equals, sharing information and decisions
# - Examples: Research tasks, brainstorming, multi-expert analysis

# ## Your Analysis Framework

# Analyze the given task and provide:
# - **Selected Architecture**: Choose ONE from the 5 options above with justification
# - **Sub-agents needed**: List in sequence/structure based on chosen architecture
# - **Tools required**: Specify tools needed for each sub-agent
# - **How sub-agents will use tools**: Detailed explanation of tool usage
# - **Workflow execution plan**: Step-by-step execution based on selected architecture
# - **Error handling approach**: Fallback strategies and recovery mechanisms

# ## Additional Guidelines

# Stick to region-friendly tools (skip anything with Chinese-language interfaces) and spell out the auth/permission steps whenever you talk about hooking apps together.

# Be specific and actionable in your response. Always justify your architecture selection based on the task characteristics and requirements."""

#     def read_prompt_from_py_file(self):

#         """Dynamically load Python file and extract 'star_output'"""

#         try:
#             spec = importlib.util.spec_from_file_location("prompt_module", self.input_file)
#             module = importlib.util.module_from_spec(spec)
#             spec.loader.exec_module(module)

#             if hasattr(module, 'star_output'):
#                 self.prompt_content = module.star_output
#                 print(f"Loaded 'star_output' from {self.input_file}")
#                 return True
#             else:
#                 print(f"'star_output' not found in {self.input_file}")
#                 return False
#         except Exception as e:
#             print(f"Error loading prompt file: {e}")
#             return False

#     def call_local_llm(self, user_prompt):

#         """Send prompt to local Ollama LLM (DeepSeek R1 7B)"""

#         try:
#             full_prompt = f"{self.system_prompt}\n\nUSER TASK:\n{user_prompt}\n\nANALYSIS:"
#             payload = {
#                 "model": "deepseek-r1:7b",
#                 "prompt": full_prompt,
#                 "stream": False
#             }

#             print("Sending prompt to Ollama...")
#             response = requests.post(self.api_url, json=payload)

#             if response.status_code == 200:
#                 result = response.json()
#                 llm_response = result.get("response", "")
#                 print("LLM response received")
#                 return llm_response
#             else:
#                 print(f"LLM API error {response.status_code}: {response.text}")
#                 return None
#         except Exception as e:
#             print(f"Failed to call LLM: {e}")
#             return None

#     def write_output(self, llm_response):
#         """Save LLM output to the specified file"""
#         try:
#             output_path = Path(self.output_file)
#             output_path.parent.mkdir(parents=True, exist_ok=True)

#             with open(output_path, 'w', encoding='utf-8') as f:
#                 f.write("BASE AGENT ANALYSIS\n")
#                 f.write("=" * 50 + "\n\n")
#                 f.write("ORIGINAL TASK:\n")
#                 f.write("-" * 20 + "\n")
#                 f.write(self.prompt_content + "\n\n")
#                 f.write("LLM ANALYSIS:\n")
#                 f.write("-" * 20 + "\n")
#                 f.write(llm_response + "\n")

#             print(f"Output saved to {self.output_file}")
#             return True
#         except Exception as e:
#             print(f"Failed to write output: {e}")
#             return False

#     def run(self):
#         """Run the whole Base Agent pipeline"""
#         print("Base Agent Starting")

#         if not self.read_prompt_from_py_file():
#             return

#         llm_response = self.call_local_llm(self.prompt_content)
#         if not llm_response:
#             return

#         if not self.write_output(llm_response):
#             return

#         print("Base Agent completed successfully!")


# def main():
   
#     input_file = "/Users/jspranav/Downloads/final_yr_project_2526/backend/v1.4/v1.4files/star_m.py"
#     output_file = "/Users/jspranav/Downloads/final_yr_project_2526/backend/v1.4/v1.4files/test_base_agent_3/base_ag_output.txt"
#     api_url = "http://localhost:11434/api/generate"  # Ollama: swap api key / url

#     agent = BaseAgent(input_file, output_file, api_url)
#     agent.run()


# if __name__ == "__main__":
#     main()




# base_agent.py - Enhanced LangGraph Version with Architecture Selection



import sys
import importlib.util
from pathlib import Path
from typing import Dict, Any, TypedDict
from datetime import datetime


from langchain_community.llms import Ollama
from langgraph.graph import StateGraph
from langchain.schema import HumanMessage

class WorkflowState(TypedDict):
    """Enhanced state for the architecture-aware workflow"""
    star_content: str
    selected_architecture: str
    architecture_justification: str
    sub_agents_analysis: str
    tools_analysis: str
    workflow_plan: str
    error_handling: str
    final_analysis: str

class BaseAgent:
    def __init__(self, input_file, output_file, api_url="http://localhost:11434/api/generate"):
        self.input_file = input_file
        self.output_file = output_file
        self.api_url = api_url
        self.prompt_content = None
        
        # Initialize LLM
        self.llm = Ollama(
            model="deepseek-r1:7b",
            base_url="http://localhost:11434"
        )
        
        # Architecture definitions (from your enhanced system prompt)
        self.architecture_options = """
## Multi-Agent Architecture Options

**1. Pipeline/Sequential**
- Use for: Linear workflows, step-by-step processes, data transformation chains
- Best when: Tasks have clear sequential dependencies (A → B → C)
- Examples: Content creation workflows, data processing pipelines, approval chains

**2. Event-Driven** 
- Use for: Reactive workflows, monitoring systems, trigger-based automation
- Best when: Tasks need to respond to events or conditions ("when X happens, do Y")
- Examples: Alert systems, conditional workflows, real-time monitoring

**3. Hierarchical**
- Use for: Complex tasks needing supervision, multi-level approval, task delegation
- Best when: Clear authority structure needed, quality control at multiple levels
- Examples: Project management, escalation workflows, multi-tier processing

**4. Hub and Spoke**
- Use for: Centralized coordination, task distribution, specialist management
- Best when: One coordinator needs to manage multiple specialist agents
- Examples: Customer service routing, resource allocation, centralized orchestration

**5. Collaborative**
- Use for: Peer-to-peer cooperation, multi-perspective analysis, consensus building
- Best when: Agents need to work together as equals, sharing information and decisions
- Examples: Research tasks, brainstorming, multi-expert analysis
"""
        
        # Build the workflow
        self.workflow = self._build_workflow()
        
        print("Enhanced LangGraph Base Agent initialized")

    def _build_workflow(self):
        """Build enhanced LangGraph workflow with architecture selection"""
        
        # Define the workflow graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("select_architecture", self._select_architecture_node)
        workflow.add_node("analyze_sub_agents", self._analyze_sub_agents_node)
        workflow.add_node("analyze_tools", self._analyze_tools_node) 
        workflow.add_node("create_workflow_plan", self._create_workflow_plan_node)
        
        # Define the flow
        workflow.set_entry_point("select_architecture")
        workflow.add_edge("select_architecture", "analyze_sub_agents")
        workflow.add_edge("analyze_sub_agents", "analyze_tools")
        workflow.add_edge("analyze_tools", "create_workflow_plan")
        workflow.set_finish_point("create_workflow_plan")
        
        return workflow.compile()

    def _select_architecture_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node 1: Select the most appropriate multi-agent architecture"""
        print("🏗️ Selecting multi-agent architecture...")
        
        prompt = f"""Based on this STAR automation task, select the BEST multi-agent architecture:

TASK: {state["star_content"]}

{self.architecture_options}

Analyze the task characteristics and select ONE architecture from the 5 options above.

Provide:
1. **Selected Architecture**: Choose ONE (Pipeline/Sequential, Event-Driven, Hierarchical, Hub and Spoke, or Collaborative)
2. **Justification**: Explain WHY this architecture fits best based on task requirements

Be specific about why other architectures wouldn't work as well.

Architecture Selection:"""
        
        response = self.llm.invoke(prompt)
        
        # Extract architecture name from response (simple parsing)
        architecture_name = "Unknown"
        if "Pipeline" in response or "Sequential" in response:
            architecture_name = "Pipeline/Sequential"
        elif "Event-Driven" in response:
            architecture_name = "Event-Driven"
        elif "Hierarchical" in response:
            architecture_name = "Hierarchical"
        elif "Hub and Spoke" in response:
            architecture_name = "Hub and Spoke"
        elif "Collaborative" in response:
            architecture_name = "Collaborative"
        
        return {
            "selected_architecture": architecture_name,
            "architecture_justification": response
        }

    def _analyze_sub_agents_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node 2: Analyze sub-agents based on selected architecture"""
        print("🤖 Analyzing sub-agents for selected architecture...")
        
        prompt = f"""Based on the selected architecture and STAR task, identify specific sub-agents needed:

TASK: {state["star_content"]}

SELECTED ARCHITECTURE: {state["selected_architecture"]}

ARCHITECTURE JUSTIFICATION: {state["architecture_justification"]}

Now design the sub-agents according to this architecture pattern:

For {state["selected_architecture"]} architecture, identify:
1. What specific sub-agents are needed
2. How they should be structured/organized according to this architecture
3. The sequence or hierarchy of sub-agents
4. Dependencies and relationships between sub-agents

Be specific about how the architecture pattern influences the sub-agent design.

Sub-agents Analysis:"""
        
        response = self.llm.invoke(prompt)
        
        return {
            "sub_agents_analysis": response
        }

    def _analyze_tools_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node 3: Analyze tools and integrations needed"""
        print("🔧 Analyzing tools and integrations...")
        
        prompt = f"""Based on the architecture and sub-agents, determine tools needed:

TASK: {state["star_content"]}

ARCHITECTURE: {state["selected_architecture"]}

SUB-AGENTS: {state["sub_agents_analysis"]}

Identify tools and integrations required:
1. Specific APIs and integrations needed
2. Authentication/permission requirements (be detailed about auth steps)
3. Region-friendly tools (avoid Chinese-language interfaces)
4. How each tool connects to the sub-agents
5. MCP tools that need to be called
6. Communication protocols between tools and agents

Focus on practical implementation details.

Tools Analysis:"""
        
        response = self.llm.invoke(prompt)
        
        return {
            "tools_analysis": response
        }

    def _create_workflow_plan_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Node 4: Create comprehensive execution plan with error handling"""
        print("📋 Creating workflow execution plan...")
        
        prompt = f"""Create a comprehensive workflow execution plan and error handling strategy:

TASK: {state["star_content"]}

ARCHITECTURE: {state["selected_architecture"]}

SUB-AGENTS: {state["sub_agents_analysis"]}

TOOLS: {state["tools_analysis"]}

Create detailed plans for:
1. **Workflow Execution Plan**: Step-by-step execution based on {state["selected_architecture"]} architecture
2. **Tool Usage**: How sub-agents will use tools to complete work
3. **Error Handling**: Fallback strategies and recovery mechanisms
4. **Success Criteria**: How to measure successful completion

Make it actionable and specific to the chosen architecture pattern.

Execution Plan:"""
        
        response = self.llm.invoke(prompt)
        
        # Create comprehensive final analysis
        final_analysis = f"""## Selected Architecture: {state["selected_architecture"]}

### Architecture Justification:
{state["architecture_justification"]}

### Sub-agents Design:
{state["sub_agents_analysis"]}

### Tools and Integrations:
{state["tools_analysis"]}

### Workflow Execution Plan:
{response}"""
        
        return {
            "workflow_plan": response,
            "error_handling": "Included in workflow plan",
            "final_analysis": final_analysis
        }

    def read_prompt_from_py_file(self):
        """Same as your original - dynamically load star_output"""
        try:
            spec = importlib.util.spec_from_file_location("prompt_module", self.input_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, 'star_output'):
                self.prompt_content = module.star_output
                print(f"Loaded 'star_output' from {self.input_file}")
                return True
            else:
                print(f"'star_output' not found in {self.input_file}")
                return False
        except Exception as e:
            print(f"Error loading prompt file: {e}")
            return False

    def run_langraph_analysis(self):
        """Run the enhanced LangGraph workflow"""
        try:
            print("Running enhanced LangGraph workflow...")
            
            # Initial state
            initial_state = {
                "star_content": self.prompt_content,
                "selected_architecture": "",
                "architecture_justification": "",
                "sub_agents_analysis": "",
                "tools_analysis": "",
                "workflow_plan": "",
                "error_handling": "",
                "final_analysis": ""
            }
            
            # Run the workflow
            result = self.workflow.invoke(initial_state)
            
            print(f"Architecture Selected: {result['selected_architecture']}")
            print("Enhanced LangGraph workflow completed")
            return result["final_analysis"]
            
        except Exception as e:
            print(f"LangGraph workflow failed: {e}")
            # Fallback to single LLM call (using your enhanced system prompt)
            return self._fallback_analysis()

    def _fallback_analysis(self):
        """Fallback using your enhanced system prompt"""
        print("Using fallback analysis with enhanced system prompt...")
        
        system_prompt = f"""You are a Base Agent in an agentic system. Your role is to:

1. Read and understand the user prompt/task
2. Maintain context throughout workflow analysis
3. Analyze tasks and determine which MCP tools need to be called
4. Manage workflow execution and coordinate tool usage
5. Handle error recovery and fallback strategies
6. Select the most appropriate multi-agent architecture for the task
7. Based on the user prompt, list out the sub-agents sequentially to fulfill the task
8. List the tools that need to be created
9. Explain how the sub-agents will use the tools to complete the work

{self.architecture_options}

## Your Analysis Framework

Analyze the given task and provide:
- **Selected Architecture**: Choose ONE from the 5 options above with justification
- **Sub-agents needed**: List in sequence/structure based on chosen architecture
- **Tools required**: Specify tools needed for each sub-agent
- **How sub-agents will use tools**: Detailed explanation of tool usage
- **Workflow execution plan**: Step-by-step execution based on selected architecture
- **Error handling approach**: Fallback strategies and recovery mechanisms

## Additional Guidelines

Stick to region-friendly tools (skip anything with Chinese-language interfaces) and spell out the auth/permission steps whenever you talk about hooking apps together.

Be specific and actionable in your response. Always justify your architecture selection based on the task characteristics and requirements."""
        
        full_prompt = f"{system_prompt}\n\nUSER TASK:\n{self.prompt_content}\n\nANALYSIS:"
        
        try:
            response = self.llm.invoke(full_prompt)
            return response
        except Exception as e:
            return f"Analysis failed: {str(e)}"

    def write_output(self, analysis_result):
        """Same output format as your original"""
        try:
            output_path = Path(self.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("BASE AGENT ANALYSIS (Enhanced LangGraph)\n")
                f.write("=" * 50 + "\n\n")
                f.write("ORIGINAL TASK:\n")
                f.write("-" * 20 + "\n")
                f.write(self.prompt_content + "\n\n")
                f.write("ENHANCED LANGGRAPH ANALYSIS:\n")
                f.write("-" * 20 + "\n")
                f.write(analysis_result + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("Agent Type: Enhanced LangGraph Workflow (Architecture Selection)\n")

            print(f"Output saved to {self.output_file}")
            return True
        except Exception as e:
            print(f"Failed to write output: {e}")
            return False

    def run(self):
        """Same interface as your original"""
        print("Enhanced LangGraph Base Agent Starting")

        # Step 1: Read STAR output (same as original)
        if not self.read_prompt_from_py_file():
            return

        # Step 2: Run enhanced LangGraph workflow  
        analysis_result = self.run_langraph_analysis()
        if not analysis_result:
            return

        # Step 3: Write output (same format as original)
        if not self.write_output(analysis_result):
            return

        print("Enhanced LangGraph Base Agent completed successfully!")


def main():
    """Same interface as your original"""
    # Update these paths to match your setup
    input_file = "/Users/jspranav/Downloads/final_yr_project_2526/backend/v2.1/star_m.py"
    output_file = "/Users/jspranav/Downloads/final_yr_project_2526/backend/v2.1/test_base_agent_4/base_ag_output.txt"
    api_url = "http://localhost:11434/api/generate"

    agent = BaseAgent(input_file, output_file, api_url)
    agent.run()


if __name__ == "__main__":
    main()