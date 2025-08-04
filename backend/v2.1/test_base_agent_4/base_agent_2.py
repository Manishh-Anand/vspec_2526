# base_agent_optimized.py - Faster & Region-Friendly
"""
Optimized LangGraph Base Agent - Faster execution, explicit anti-Chinese tools
"""
import sys
import importlib.util
from pathlib import Path
from typing import Dict, Any, TypedDict
from datetime import datetime

from langchain_ollama import Ollama
from langgraph.graph import StateGraph
from langchain.schema import HumanMessage

class WorkflowState(TypedDict):
    """Simplified state for faster workflow"""
    star_content: str
    architecture_analysis: str
    implementation_plan: str
    final_analysis: str

class BaseAgent:
    def __init__(self, input_file, output_file, api_url="http://localhost:11434/api/generate"):
        self.input_file = input_file
        self.output_file = output_file
        self.api_url = api_url
        self.prompt_content = None
        
        # Initialize LLM with faster settings
        self.llm = Ollama(
            model="deepseek-r1:7b",
            base_url="http://localhost:11434",
            temperature=0.3,  # Lower for consistency and speed
        )
        
        # Build the optimized workflow (only 2 nodes instead of 4)
        self.workflow = self._build_workflow()
        
        print("Optimized LangGraph Base Agent initialized")

    def _build_workflow(self):
        """Build optimized 2-node workflow for speed"""
        
        workflow = StateGraph(WorkflowState)
        
        # Only 2 nodes for speed
        workflow.add_node("architecture_analysis", self._architecture_analysis_node)
        workflow.add_node("implementation_plan", self._implementation_plan_node)
        
        # Simple linear flow
        workflow.set_entry_point("architecture_analysis")
        workflow.add_edge("architecture_analysis", "implementation_plan")
        workflow.set_finish_point("implementation_plan")
        
        return workflow.compile()

    def _architecture_analysis_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Combined Node 1: Architecture Selection + Sub-agents (faster)"""
        print("🏗️ Analyzing architecture and sub-agents...")
        
        prompt = f"""Analyze this automation task and select architecture + sub-agents:

TASK: {state["star_content"]}

**CRITICAL: Only suggest Western/US-based tools. NO Chinese tools, apps, or interfaces.**

## Architecture Options:
1. **Pipeline/Sequential** - Linear A→B→C workflows
2. **Event-Driven** - "When X happens, do Y" reactive systems  
3. **Hierarchical** - Multi-level supervision
4. **Hub and Spoke** - Central coordinator with specialists
5. **Collaborative** - Peer-to-peer cooperation

## Required Output:
**Selected Architecture:** [Pick ONE from above]
**Why This Architecture:** [Brief justification]
**Sub-agents Needed:** [List 2-4 specific agents in order]
**Agent Relationships:** [How they connect/communicate]


NO Chinese platforms, apps, or services.

Keep response concise but complete.

Analysis:"""
        
        response = self.llm.invoke(prompt)
        
        return {
            "architecture_analysis": response
        }

    def _implementation_plan_node(self, state: WorkflowState) -> Dict[str, Any]:
        """Combined Node 2: Tools + Implementation (faster)"""
        print("🔧 Creating implementation plan...")
        
        prompt = f"""Create implementation plan based on architecture analysis:

TASK: {state["star_content"]}

ARCHITECTURE ANALYSIS: {state["architecture_analysis"]}

**CRITICAL: Only use Western/global tools. Absolutely NO Chinese tools or platforms.**

## Required Output:
**Tools Required:** [Specific APIs/integrations - only Western/global tools]
**Authentication Steps:** [Detailed auth/permission requirements]
**Workflow Steps:** [Step-by-step execution plan]
**Error Handling:** [Fallback strategies]

**Western Tools Only Examples:**
- Google APIs (Gmail, Calendar, Drive, Meet)
- Microsoft (Outlook, Teams, Office 365)
- Slack, Discord, Zoom
- GitHub, GitLab
- AWS, Azure services
- Zapier, IFTTT
- Trello, Asana, Notion

**Avoid anything Chinese-language or China-based.**

Keep response focused and actionable.

Implementation Plan:"""
        
        response = self.llm.invoke(prompt)
        
        # Combine everything for final output
        final_analysis = f"""## Architecture & Sub-agents Analysis:
{state["architecture_analysis"]}

## Implementation Plan:
{response}"""
        
        return {
            "implementation_plan": response,
            "final_analysis": final_analysis
        }

    def read_prompt_from_py_file(self):
        """Same as original - load star_output"""
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
        """Run optimized 2-node workflow"""
        try:
            print("Running optimized LangGraph workflow...")
            
            # Simplified initial state
            initial_state = {
                "star_content": self.prompt_content,
                "architecture_analysis": "",
                "implementation_plan": "",
                "final_analysis": ""
            }
            
            # Run the workflow (only 2 LLM calls instead of 4)
            result = self.workflow.invoke(initial_state)
            
            print("Optimized LangGraph workflow completed")
            return result["final_analysis"]
            
        except Exception as e:
            print(f"LangGraph workflow failed: {e}")
            return self._fallback_analysis()

    def _fallback_analysis(self):
        """Optimized fallback with anti-Chinese emphasis"""
        print("Using optimized fallback analysis...")
        
        system_prompt = f"""You are a Base Agent for automation analysis.

**CRITICAL REQUIREMENT: DO NOT USE Chinese tools, apps, or platforms.**

Analyze the task and provide:
1. **Architecture Selection**: Choose from Pipeline, Event-Driven, Hierarchical, Hub-and-Spoke, or Collaborative
2. **Sub-agents**: List 2-4 specific agents needed
3. **Tools needed**: APIs/integrations 
4. **Implementation**: Step-by-step plan with auth details
5. **Error Handling**: Fallback strategies


**NEVER suggest Chinese platforms or tools.**

Be concise but thorough."""
        
        full_prompt = f"{system_prompt}\n\nTASK:\n{self.prompt_content}\n\nANALYSIS:"
        
        try:
            response = self.llm.invoke(full_prompt)
            return response
        except Exception as e:
            return f"Analysis failed: {str(e)}"

    def write_output(self, analysis_result):
        """Same output format"""
        try:
            output_path = Path(self.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("BASE AGENT ANALYSIS (Optimized LangGraph)\n")
                f.write("=" * 50 + "\n\n")
                f.write("ORIGINAL TASK:\n")
                f.write("-" * 20 + "\n")
                f.write(self.prompt_content + "\n\n")
                f.write("OPTIMIZED LANGGRAPH ANALYSIS:\n")
                f.write("-" * 20 + "\n")
                f.write(analysis_result + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("Agent Type: Optimized LangGraph (2-Node, Western Tools Only)\n")

            print(f"Output saved to {self.output_file}")
            return True
        except Exception as e:
            print(f"Failed to write output: {e}")
            return False

    def run(self):
        """Same interface"""
        print("Optimized LangGraph Base Agent Starting")

        if not self.read_prompt_from_py_file():
            return

        analysis_result = self.run_langraph_analysis()
        if not analysis_result:
            return

        if not self.write_output(analysis_result):
            return

        print("Optimized LangGraph Base Agent completed successfully!")


def main():
    """Same interface"""
    input_file = "/Users/jspranav/Downloads/final_yr_project_2526/backend/v2.1/star_m.py"
    output_file = "/Users/jspranav/Downloads/final_yr_project_2526/backend/v2.1/test_base_agent_4/base_ag_output.txt"
    api_url = "http://localhost:11434/api/generate"

    agent = BaseAgent(input_file, output_file, api_url)
    agent.run()


if __name__ == "__main__":
    main()