#!/usr/bin/env python3
"""
Workflow Coordinator for: workflow_20250812_195444
Domain: finance
Generated at: 2025-09-07T18:05:59.056202
"""

import asyncio
from pathlib import Path
import sys
import json

# Ensure the generated agents in this directory can be imported
sys.path.append(str(Path(__file__).parent))

# Dynamically import the UniversalAgent class from each generated agent file
from agent_1 import UniversalAgent as Agent_1
from agent_2 import UniversalAgent as Agent_2
from agent_3 import UniversalAgent as Agent_3
from agent_4 import UniversalAgent as Agent_4
from agent_5 import UniversalAgent as Agent_5

class WorkflowCoordinator:
    """Manages the sequential execution of the multi-agent workflow."""
    
    def __init__(self):
        self.workflow_meta = {
            "workflow_id": "workflow_20250812_195444",
            "workflow_name": "Unknown Workflow",
            "domain": "finance",
            "version": "1.0.0",
            "description": "",
            "created_by": "mcp-module",
            "created_at": "2025-08-31T10:41:15.468750",
            "mcp_module_version": "1.0.0",
            "protocol_version": "2024-11-05"
}
        self.agents = {
            "agent_1": Agent_1(),
            "agent_2": Agent_2(),
            "agent_3": Agent_3(),
            "agent_4": Agent_4(),
            "agent_5": Agent_5(),
        }
        self.orchestration_config = {
            "strategy": "sequential",
            "parallel_execution": False,
            "error_handling": "stop_on_error",
            "retry_policy": {},
            "timeout": 300,
            "dependencies": []
}
        self.agent_order = sorted(['agent_1', 'agent_2', 'agent_3', 'agent_4', 'agent_5'])
        
    async def execute(self, initial_input: dict):
        """Executes the workflow from start to finish."""
        current_data = initial_input
        print(f"--- Starting Workflow: {self.workflow_meta.get('workflow_id')} ---")
        
        # Simple sequential execution based on sorted agent_id
        for agent_id in self.agent_order:
            if agent_id not in self.agents:
                print(f"!! Warning: Agent '{agent_id}' not found, skipping.")
                continue

            agent_instance = self.agents[agent_id]
            print(f"\n>>> Executing Agent: {agent_instance.agent_name} ({agent_id})")
            
            try:
                result = await agent_instance.process(current_data)
                
                if result.get("status") == "failure":
                    print(f"X Agent {agent_id} reported a failure: {result.get('error')}")
                    if self.orchestration_config.get("error_handling") == "stop_on_error":
                        print("--- Workflow Halted Due to Error ---")
                        return result
                else:
                    print(f"OK Agent {agent_id} completed successfully.")

                current_data = result # Pass the full output of one agent to the next
            
            except Exception as e:
                print(f"X An unexpected exception occurred in {agent_id}: {e}")
                if self.orchestration_config.get("error_handling") == "stop_on_error":
                    raise
        
        print("\n--- Workflow Completed ---")
        return current_data

if __name__ == "__main__":
    coordinator = WorkflowCoordinator()
    
    # Define the initial input that starts the workflow
    initial_workflow_input = {
        "message": "Start the financial analysis process based on the provided bank statements.",
        "data": { "source_file": "/path/to/your/bank_statement.csv" },
        "timestamp": "2025-09-07T18:05:59.056202"
    }
    
    final_result = asyncio.run(coordinator.execute(initial_workflow_input))
    
    print("\nFinal Workflow Result:")
    print(json.dumps(final_result, indent=2))
