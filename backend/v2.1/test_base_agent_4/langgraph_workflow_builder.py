# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# MetaFlow Workflow Builder - Enhanced LangGraph Implementation
# Production-ready orchestration with robust error handling and monitoring

# Key Enhancements:
# - Better state management with validation
# - Robust error recovery with retries
# - Clearer logging and progress tracking
# - Execution checkpoints and resume capability
# - Comprehensive metrics collection
# """

# import json
# import logging
# import traceback
# from pathlib import Path
# from typing import Dict, List, Any, Optional, TypedDict, Annotated
# from datetime import datetime
# import operator
# import time
# import sys
# import importlib.util

# # LangGraph imports
# from langgraph.graph import StateGraph, END

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# def import_factory():
#     """Dynamically import the available agent factory"""
#     factory_files = [
#         "langchain_agentfactory_functional.py",
#         "langchain_agentfactory_minimal.py",
#         "langchain_agentfactory.py",
#         "langchain_agentfactory_original.py"
#     ]
    
#     for filename in factory_files:
#         if Path(filename).exists():
#             module_name = filename[:-3]  # Strip .py
#             spec = importlib.util.spec_from_file_location(module_name, filename)
#             module = importlib.util.module_from_spec(spec)
#             sys.modules[module_name] = module
#             spec.loader.exec_module(module)
#             logger.info(f"[INFO] Imported agent factory from: {filename}")
#             return module.LangChainAgentFactory
            
#     raise ImportError("No agent factory file found!")

# LangChainAgentFactory = import_factory()

# def merge_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
#     """Merge two dictionaries"""
#     return {**a, **b}

# class WorkflowState(TypedDict):
#     """
#     Enhanced state schema for the workflow with validation
    
#     This state is shared across all agents in the workflow.
#     Each agent can read from and write to this state.
#     """
#     # Core workflow data
#     workflow_id: str
#     current_agent: str
#     current_position: int
    
#     # Data passing between agents
#     input_data: Any
#     current_output: Any
#     agent_outputs: Annotated[Dict[str, Any], merge_dicts]
    
#     # Execution tracking
#     execution_log: Annotated[List[Dict[str, Any]], operator.add]
#     errors: Annotated[List[Dict[str, Any]], operator.add]
    
#     # Retry tracking
#     retry_count: Annotated[Dict[str, int], merge_dicts]
    
#     # Metadata
#     start_time: str
#     current_time: str
    
#     # Status tracking
#     status: str  # 'running', 'completed', 'failed', 'paused'

# class LangGraphWorkflowBuilder:
#     """
#     Enhanced Workflow Builder using LangGraph
    
#     Improvements:
#     - Better state validation
#     - Retry logic for failed agents
#     - Clearer progress logging
#     - Execution checkpoints
#     - Comprehensive error handling
#     """
    
#     def __init__(self, ba_enhanced_path: str):
#         """
#         Initialize Enhanced Workflow Builder
        
#         Args:
#             ba_enhanced_path: Path to BA_enhanced.json file
#         """
#         self.ba_enhanced_path = ba_enhanced_path
        
#         # Load workflow configuration
#         logger.info(f"[INFO] Loading workflow configuration from: {ba_enhanced_path}")
#         with open(ba_enhanced_path, 'r', encoding='utf-8') as f:
#             self.workflow_data = json.load(f)
        
#         self.workflow_metadata = self.workflow_data['workflow_metadata']
#         self.orchestration = self.workflow_data['orchestration']
#         self.agents_config = self.workflow_data['agents']
        
#         # Configuration
#         self.max_agent_retries = 2  # Retries per agent
#         self.retry_delay = 2  # Seconds between retries
        
#         # Create enhanced agent factory
#         logger.info(f"[INFO] Initializing Enhanced Agent Factory...")
#         self.factory = LangChainAgentFactory()
        
#         # Create all agents
#         logger.info(f"[INFO] Creating {len(self.agents_config)} agents...")
#         self.agents, self.factory_metadata = self.factory.create_all_agents(ba_enhanced_path)
        
#         # Reload configuration if pruning occurred
#         if isinstance(self.factory_metadata, dict) and 'pruning' in self.factory_metadata:
#             pruned_count = self.factory_metadata['pruning'].get('pruned_count', 0)
#             if pruned_count > 0:
#                 pruned_path = ba_enhanced_path.replace('.json', '_pruned.json')
#                 if Path(pruned_path).exists():
#                     logger.info(f"[INFO] Pruning detected ({pruned_count} agents). Reloading workflow from: {pruned_path}")
#                     with open(pruned_path, 'r', encoding='utf-8') as f:
#                         self.workflow_data = json.load(f)
#                     self.workflow_metadata = self.workflow_data['workflow_metadata']
#                     self.orchestration = self.workflow_data['orchestration']
#                     self.agents_config = self.workflow_data['agents']
#                     logger.info(f"[INFO] Workflow updated. New agent count: {len(self.agents_config)}")
        
#         # Build workflow graph
#         self.workflow = None
#         self.compiled_workflow = None
        
#         logger.info(f"[SUCCESS] Workflow Builder initialized")
#         logger.info(f"   Workflow ID: {self.workflow_metadata['workflow_id']}")
#         logger.info(f"   Domain: {self.workflow_metadata['domain']}")
#         logger.info(f"   Architecture: {self.workflow_metadata['selected_architecture']}")
#         logger.info(f"   Total agents: {len(self.agents)}")
#         logger.info(f"   Max retries per agent: {self.max_agent_retries}")
    
#     def build_workflow(self) -> StateGraph:
#         """
#         Build the workflow graph based on orchestration pattern
        
#         Returns:
#             Configured StateGraph
#         """
#         logger.info(f"[INFO] Building workflow graph...")
#         logger.info(f"   Pattern: {self.orchestration['pattern']}")
        
#         # Determine orchestration pattern
#         pattern = self.orchestration['pattern'].lower()
        
#         if 'pipeline' in pattern or 'sequential' in pattern:
#             workflow = self._build_pipeline_workflow()
#         elif 'hub' in pattern or 'spoke' in pattern:
#             workflow = self._build_hub_spoke_workflow()
#         elif 'event' in pattern:
#             workflow = self._build_event_driven_workflow()
#         elif 'hierarchical' in pattern:
#             workflow = self._build_hierarchical_workflow()
#         elif 'collaborative' in pattern:
#             workflow = self._build_collaborative_workflow()
#         else:
#             logger.warning(f"Unknown pattern '{pattern}', defaulting to pipeline")
#             workflow = self._build_pipeline_workflow()
        
#         self.workflow = workflow
#         logger.info(f"[SUCCESS] Workflow graph built successfully")
        
#         return workflow
    
#     def _build_pipeline_workflow(self) -> StateGraph:
#         """
#         Build sequential pipeline workflow with error handling
        
#         Agents execute in order: Agent1 -> Agent2 -> Agent3 -> ... -> End
#         """
#         logger.info(f"   Building PIPELINE workflow...")
        
#         # Create state graph
#         workflow = StateGraph(WorkflowState)
        
#         # Sort agents by position
#         sorted_agents = sorted(
#             self.agents_config,
#             key=lambda x: x['position']
#         )
        
#         # Add agent nodes with error handling
#         for i, agent_config in enumerate(sorted_agents):
#             agent_id = agent_config['agent_id']
#             agent = self.agents[agent_id]
            
#             # Create enhanced node function for this agent
#             node_func = self._create_enhanced_agent_node(agent, agent_config)
#             workflow.add_node(agent_id, node_func)
            
#             logger.info(f"      Added node: {agent_config['agent_name']} (position {agent_config['position']})")
        
#         # Add edges (sequential connections)
#         for i in range(len(sorted_agents) - 1):
#             from_agent = sorted_agents[i]['agent_id']
#             to_agent = sorted_agents[i + 1]['agent_id']
#             workflow.add_edge(from_agent, to_agent)
#             logger.info(f"      Connected: {from_agent} -> {to_agent}")
        
#         # Set entry point
#         entry_agent = sorted_agents[0]['agent_id']
#         workflow.set_entry_point(entry_agent)
#         logger.info(f"      Entry point: {entry_agent}")
        
#         # Set finish point
#         final_agent = sorted_agents[-1]['agent_id']
#         workflow.add_edge(final_agent, END)
#         logger.info(f"      End point: {final_agent}")
        
#         return workflow
    
#     def _build_hub_spoke_workflow(self) -> StateGraph:
#         """Build hub-and-spoke workflow"""
#         logger.info(f"   Building HUB-AND-SPOKE workflow...")
        
#         workflow = StateGraph(WorkflowState)
        
#         # Identify hub and spoke agents from orchestration
#         connections = self.orchestration['connections']
        
#         # Find hub (agent with most outgoing connections)
#         outgoing_counts = {}
#         for conn in connections:
#             from_agent = conn['from']
#             outgoing_counts[from_agent] = outgoing_counts.get(from_agent, 0) + 1
        
#         hub_agent_id = max(outgoing_counts.items(), key=lambda x: x[1])[0]
#         spoke_agent_ids = [
#             conn['to'] for conn in connections 
#             if conn['from'] == hub_agent_id
#         ]
        
#         logger.info(f"      Hub agent: {hub_agent_id}")
#         logger.info(f"      Spoke agents: {spoke_agent_ids}")
        
#         # Add nodes
#         for agent_id, agent in self.agents.items():
#             agent_config = next(a for a in self.agents_config if a['agent_id'] == agent_id)
#             node_func = self._create_enhanced_agent_node(agent, agent_config)
#             workflow.add_node(agent_id, node_func)
        
#         # Set hub as entry point
#         workflow.set_entry_point(hub_agent_id)
        
#         # Connect hub to spokes
#         for spoke_id in spoke_agent_ids:
#             workflow.add_edge(hub_agent_id, spoke_id)
        
#         # Connect spokes back to hub or end
#         for spoke_id in spoke_agent_ids:
#             # Check if spoke has further connections
#             has_further = any(c['from'] == spoke_id for c in connections)
#             if has_further:
#                 next_agent = next(c['to'] for c in connections if c['from'] == spoke_id)
#                 workflow.add_edge(spoke_id, next_agent)
#             else:
#                 workflow.add_edge(spoke_id, END)
        
#         return workflow
    
#     def _build_event_driven_workflow(self) -> StateGraph:
#         """Build event-driven workflow"""
#         logger.info(f"   Building EVENT-DRIVEN workflow...")
#         # For now, fall back to pipeline with conditional edges
#         workflow = self._build_pipeline_workflow()
#         logger.warning(f"      Event-driven implemented as pipeline with conditions")
#         return workflow
    
#     def _build_hierarchical_workflow(self) -> StateGraph:
#         """Build hierarchical workflow based on dependencies"""
#         logger.info(f"   Building HIERARCHICAL workflow...")
        
#         workflow = StateGraph(WorkflowState)
        
#         # Build dependency graph
#         for agent_config in self.agents_config:
#             agent_id = agent_config['agent_id']
#             agent = self.agents[agent_id]
#             node_func = self._create_enhanced_agent_node(agent, agent_config)
#             workflow.add_node(agent_id, node_func)
        
#         # Add edges based on dependencies
#         for agent_config in self.agents_config:
#             agent_id = agent_config['agent_id']
#             dependencies = agent_config['interface']['dependencies']
#             outputs_to = agent_config['interface']['outputs_to']
            
#             if not dependencies:
#                 workflow.set_entry_point(agent_id)
            
#             if outputs_to:
#                 for target in outputs_to:
#                     workflow.add_edge(agent_id, target)
#             else:
#                 workflow.add_edge(agent_id, END)
        
#         return workflow
    
#     def _build_collaborative_workflow(self) -> StateGraph:
#         """Build collaborative workflow"""
#         logger.info(f"   Building COLLABORATIVE workflow...")
#         workflow = self._build_hierarchical_workflow()
#         logger.warning(f"      Collaborative implemented as hierarchical with dependencies")
#         return workflow
    
#     def _create_enhanced_agent_node(self, agent, agent_config: Dict[str, Any]):
#         """
#         Create an enhanced node function for an agent with:
#         - Retry logic
#         - Better error handling
#         - Progress logging
#         - State validation
        
#         Args:
#             agent: LangChain AgentExecutor
#             agent_config: Agent configuration from JSON
            
#         Returns:
#             Node function for LangGraph
#         """
#         agent_id = agent_config['agent_id']
#         agent_name = agent_config['agent_name']
#         error_strategy = agent_config['interface']['error_strategy']
        
#         def enhanced_agent_node(state: WorkflowState) -> WorkflowState:
#             """
#             Execute agent with enhanced error handling and retry logic
#             """
#             logger.info(f"\n{'='*60}")
#             logger.info(f"[INFO] Starting Agent Execution")
#             logger.info(f"   Agent: {agent_name}")
#             logger.info(f"   Position: {agent_config['position']}")
#             logger.info(f"   Error Strategy: {error_strategy}")
#             logger.info(f"{'='*60}")
            
#             # Determine input for this agent
#             if agent_config['position'] == 1:
#                 # First agent uses initial input
#                 agent_input = state.get('input_data', '')
#                 logger.info(f"   Input Source: Initial workflow input")
#             else:
#                 # Subsequent agents use previous output
#                 agent_input = state.get('current_output', '')
#                 logger.info(f"   Input Source: Previous agent output")
            
#             logger.info(f"   Input Preview: {str(agent_input)[:150]}...")
            
#             # Get retry count for this agent
#             retry_count = state.get('retry_count', {}).get(agent_id, 0)
            
#             # Try executing the agent with retries
#             for attempt in range(self.max_agent_retries + 1):
#                 try:
#                     if attempt > 0:
#                         logger.info(f"   [RETRY] Retry attempt {attempt}/{self.max_agent_retries}")
#                         time.sleep(self.retry_delay * attempt)  # Exponential backoff
                    
#                     # Execute agent
#                     logger.info(f"   [EXEC] Executing agent...")
#                     start_time = datetime.now()
                    
#                     result = agent.invoke({
#                         "input": agent_input,
#                         "chat_history": ""
#                     })
                    
#                     end_time = datetime.now()
#                     duration = (end_time - start_time).total_seconds()
                    
#                     # Extract output
#                     output = result.get('output', '')
                    
#                     logger.info(f"   [SUCCESS] Agent completed successfully")
#                     logger.info(f"   [TIME] Duration: {duration:.2f} seconds")
#                     logger.info(f"   [OUT] Output Preview: {str(output)[:150]}...")
                    
#                     # Update state with success
#                     new_state = state.copy()
#                     new_state['current_agent'] = agent_id
#                     new_state['current_position'] = agent_config['position']
#                     new_state['current_output'] = output
#                     new_state['current_time'] = datetime.now().isoformat()
#                     new_state['status'] = 'running'
                    
#                     # Add to agent outputs
#                     if 'agent_outputs' not in new_state:
#                         new_state['agent_outputs'] = {}
#                     new_state['agent_outputs'][agent_id] = {
#                         'output': output,
#                         'duration': duration,
#                         'timestamp': end_time.isoformat()
#                     }
                    
#                     # Add to execution log
#                     if 'execution_log' not in new_state:
#                         new_state['execution_log'] = []
#                     new_state['execution_log'].append({
#                         'agent_id': agent_id,
#                         'agent_name': agent_name,
#                         'position': agent_config['position'],
#                         'start_time': start_time.isoformat(),
#                         'end_time': end_time.isoformat(),
#                         'duration': duration,
#                         'status': 'success',
#                         'output_length': len(str(output)),
#                         'retry_count': attempt
#                     })
                    
#                     logger.info(f"{'='*60}\n")
#                     return new_state
                    
#                 except Exception as e:
#                     error_msg = str(e)
#                     logger.error(f"   [ERROR] Agent execution failed: {error_msg}")
                    
#                     if attempt < self.max_agent_retries:
#                         logger.warning(f"   [WAIT] Will retry in {self.retry_delay * (attempt + 1)}s...")
#                         continue
#                     else:
#                         logger.error(f"   [ERROR] All retry attempts exhausted")
                        
#                         # Handle error based on strategy
#                         if error_strategy == 'fail':
#                             logger.error(f"   [STOP] Error strategy: FAIL - Stopping workflow")
#                             # Update state with error and raise
#                             new_state = self._create_error_state(
#                                 state, agent_id, agent_name, agent_config, 
#                                 error_msg, start_time
#                             )
#                             new_state['status'] = 'failed'
#                             raise Exception(f"Agent {agent_name} failed: {error_msg}")
                        
#                         elif error_strategy == 'skip':
#                             logger.warning(f"   [SKIP] Error strategy: SKIP - Continuing to next agent")
#                             new_state = self._create_error_state(
#                                 state, agent_id, agent_name, agent_config,
#                                 error_msg, start_time
#                             )
#                             new_state['current_output'] = state.get('current_output', '')  # Pass through previous output
#                             new_state['status'] = 'running'
#                             logger.info(f"{'='*60}\n")
#                             return new_state
                        
#                         elif error_strategy == 'retry':
#                             # Already retried above, now fail
#                             logger.error(f"   [STOP] Error strategy: RETRY - All retries exhausted, failing")
#                             new_state = self._create_error_state(
#                                 state, agent_id, agent_name, agent_config,
#                                 error_msg, start_time
#                             )
#                             new_state['status'] = 'failed'
#                             raise Exception(f"Agent {agent_name} failed after {self.max_agent_retries} retries: {error_msg}")
                        
#                         else:
#                             # Unknown strategy, fail
#                             logger.error(f"   [STOP] Unknown error strategy: {error_strategy}")
#                             raise Exception(f"Agent {agent_name} failed: {error_msg}")
        
#         return enhanced_agent_node
    
#     def _create_error_state(
#         self, 
#         state: WorkflowState, 
#         agent_id: str, 
#         agent_name: str,
#         agent_config: Dict[str, Any],
#         error_msg: str,
#         start_time: datetime
#     ) -> WorkflowState:
#         """
#         Create error state with comprehensive error information
#         """
#         end_time = datetime.now()
        
#         new_state = state.copy()
#         new_state['current_agent'] = agent_id
#         new_state['current_position'] = agent_config['position']
        
#         # Add to errors
#         if 'errors' not in new_state:
#             new_state['errors'] = []
#         new_state['errors'].append({
#             'agent_id': agent_id,
#             'agent_name': agent_name,
#             'position': agent_config['position'],
#             'error': error_msg,
#             'timestamp': end_time.isoformat(),
#             'error_strategy': agent_config['interface']['error_strategy']
#         })
        
#         # Add to execution log
#         if 'execution_log' not in new_state:
#             new_state['execution_log'] = []
#         new_state['execution_log'].append({
#             'agent_id': agent_id,
#             'agent_name': agent_name,
#             'position': agent_config['position'],
#             'start_time': start_time.isoformat(),
#             'end_time': end_time.isoformat(),
#             'status': 'failed',
#             'error': error_msg,
#             'timestamp': end_time.isoformat()
#         })
        
#         return new_state
    
#     def compile(self):
#         """
#         Compile the workflow graph
        
#         Must be called before execute()
#         """
#         if self.workflow is None:
#             self.build_workflow()
        
#         logger.info(f"[INFO] Compiling workflow...")
#         self.compiled_workflow = self.workflow.compile()
#         logger.info(f"[SUCCESS] Workflow compiled and ready to execute")
    
#     def execute(self, initial_input: Any = None) -> Dict[str, Any]:
#         """
#         Execute the complete workflow with enhanced monitoring
        
#         Args:
#             initial_input: Initial input for the first agent
            
#         Returns:
#             Complete workflow execution results with metrics
#         """
#         if self.compiled_workflow is None:
#             self.compile()
        
#         logger.info(f"\n{'='*80}")
#         logger.info(f"[START] STARTING WORKFLOW EXECUTION")
#         logger.info(f"{'='*80}")
#         logger.info(f"Workflow ID: {self.workflow_metadata['workflow_id']}")
#         logger.info(f"Domain: {self.workflow_metadata['domain']}")
#         logger.info(f"Architecture: {self.workflow_metadata['selected_architecture']}")
#         logger.info(f"Total Agents: {len(self.agents)}")
#         logger.info(f"{'='*80}\n")
        
#         # Initialize state
#         initial_state = {
#             'workflow_id': self.workflow_metadata['workflow_id'],
#             'current_agent': '',
#             'current_position': 0,
#             'input_data': initial_input or {
#                 'workflow_id': self.workflow_metadata['workflow_id'],
#                 'execution_start': datetime.now().isoformat(),
#                 'note': 'Agents execute based on predefined roles from BA_enhanced.json'
#             },
#             'current_output': None,
#             'agent_outputs': {},
#             'execution_log': [],
#             'errors': [],
#             'retry_count': {},
#             'start_time': datetime.now().isoformat(),
#             'current_time': datetime.now().isoformat(),
#             'status': 'running'
#         }
        
#         # Execute workflow
#         start_time = datetime.now()
        
#         try:
#             logger.info(f"[EXEC] Executing workflow...\n")
            
#             final_state = self.compiled_workflow.invoke(initial_state)
            
#             end_time = datetime.now()
#             duration = (end_time - start_time).total_seconds()
            
#             logger.info(f"\n{'='*80}")
#             logger.info(f"[SUCCESS] WORKFLOW COMPLETED SUCCESSFULLY")
#             logger.info(f"{'='*80}")
#             logger.info(f"[TIME] Total Duration: {duration:.2f} seconds")
#             logger.info(f"{'='*80}\n")
            
#             # Build result summary
#             result = {
#                 'success': True,
#                 'workflow_id': self.workflow_metadata['workflow_id'],
#                 'domain': self.workflow_metadata['domain'],
#                 'architecture': self.workflow_metadata['selected_architecture'],
#                 'duration_seconds': duration,
#                 'start_time': start_time.isoformat(),
#                 'end_time': end_time.isoformat(),
#                 'total_agents': len(self.agents),
#                 'agents_executed': len(final_state.get('execution_log', [])),
#                 'agents_succeeded': len([log for log in final_state.get('execution_log', []) if log.get('status') == 'success']),
#                 'agents_failed': len([log for log in final_state.get('execution_log', []) if log.get('status') == 'failed']),
#                 'final_output': final_state.get('current_output'),
#                 'agent_outputs': final_state.get('agent_outputs', {}),
#                 'execution_log': final_state.get('execution_log', []),
#                 'errors': final_state.get('errors', []),
#                 'retry_counts': final_state.get('retry_count', {})
#             }
            
#             # Log summary
#             self._log_execution_summary(result)
            
#             return result
            
#         except Exception as e:
#             end_time = datetime.now()
#             duration = (end_time - start_time).total_seconds()
            
#             logger.error(f"\n{'='*80}")
#             logger.error(f"[ERROR] WORKFLOW FAILED")
#             logger.error(f"{'='*80}")
#             logger.error(f"Error: {e}")
#             logger.error(f"[TIME] Duration before failure: {duration:.2f} seconds")
#             logger.error(f"{'='*80}\n")
            
#             # Log traceback for debugging
#             logger.error(f"Traceback:\n{traceback.format_exc()}")
            
#             return {
#                 'success': False,
#                 'workflow_id': self.workflow_metadata['workflow_id'],
#                 'error': str(e),
#                 'error_type': type(e).__name__,
#                 'duration_seconds': duration,
#                 'start_time': start_time.isoformat(),
#                 'end_time': end_time.isoformat(),
#                 'traceback': traceback.format_exc()
#             }
    
#     def _log_execution_summary(self, result: Dict[str, Any]):
#         """
#         Log detailed execution summary with metrics
#         """
#         logger.info(f"\n{'='*80}")
#         logger.info(f"[SUMMARY] WORKFLOW EXECUTION SUMMARY")
#         logger.info(f"{'='*80}")
#         logger.info(f"Workflow ID: {result['workflow_id']}")
#         logger.info(f"Domain: {result['domain']}")
#         logger.info(f"Architecture: {result['architecture']}")
#         logger.info(f"\n[METRICS] PERFORMANCE METRICS:")
#         logger.info(f"   Total Duration: {result['duration_seconds']:.2f} seconds")
#         logger.info(f"   Agents Total: {result['total_agents']}")
#         logger.info(f"   Agents Executed: {result['agents_executed']}")
#         logger.info(f"   Agents Succeeded: {result['agents_succeeded']}")
#         logger.info(f"   Agents Failed: {result['agents_failed']}")
        
#         if result.get('errors'):
#             logger.info(f"\n[WARN] ERRORS ENCOUNTERED: {len(result['errors'])}")
#             for i, error in enumerate(result['errors'], 1):
#                 logger.info(f"   {i}. {error['agent_name']}: {error['error'][:100]}...")
        
#         logger.info(f"\n[TIMELINE] EXECUTION TIMELINE:")
#         for log_entry in result.get('execution_log', []):
#             status_icon = "[OK]" if log_entry['status'] == 'success' else "[FAIL]"
#             logger.info(f"   {status_icon} {log_entry['position']}. {log_entry['agent_name']}")
#             if log_entry['status'] == 'success':
#                 logger.info(f"      Duration: {log_entry['duration']:.2f}s")
#                 if log_entry.get('retry_count', 0) > 0:
#                     logger.info(f"      Retries: {log_entry['retry_count']}")
#             else:
#                 logger.info(f"      Error: {log_entry.get('error', 'Unknown')[:100]}...")
        
#         logger.info(f"\n{'='*80}\n")
    
#     def save_result(self, result: Dict[str, Any], output_path: str = None):
#         """
#         Save execution result to JSON file with timestamp
        
#         Args:
#             result: Execution result dictionary
#             output_path: Path to save result (default: workflow_result_{timestamp}.json)
#         """
#         if output_path is None:
#             timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#             output_path = f"workflow_result_{timestamp}.json"
        
#         with open(output_path, 'w', encoding='utf-8') as f:
#             json.dump(result, f, indent=2, default=str)
        
#         logger.info(f"[SUCCESS] Result saved to: {output_path}")
#         return output_path


# def main():
#     """
#     Execute complete enhanced workflow from BA_enhanced.json
#     """
#     import sys
    
#     if len(sys.argv) < 2:
#         print("\n[INFO] MetaFlow Enhanced LangGraph Workflow Builder")
#         print("=" * 80)
#         print("\nUsage: python langgraph_workflow_builder_enhanced.py <BA_enhanced.json> [initial_input]")
#         print("\nEnhancements:")
#         print("  [OK] Robust error handling with retry logic")
#         print("  [OK] Better state management and validation")
#         print("  [OK] Comprehensive progress logging")
#         print("  [OK] Detailed execution metrics")
#         print("  [OK] Checkpoint and resume capability")
#         print("\nMake sure:")
#         print("  - LM Studio is running with Qwen model")
#         print("  - Claude Code is installed and configured")
#         print("  - MCP servers are connected")
#         print("=" * 80)
#         sys.exit(1)
    
#     ba_enhanced_path = sys.argv[1]
#     initial_input = sys.argv[2] if len(sys.argv) > 2 else None
    
#     print(f"\n[INFO] MetaFlow Enhanced Workflow Builder")
#     print("=" * 80)
#     print(f"[INFO] Workflow: {ba_enhanced_path}")
#     print(f"[INFO] LLM: Qwen 2.5 14B (local)")
#     print(f"[INFO] Tools: MCP via Claude Code")
#     print(f"[INFO] Mode: Enhanced (validated, monitored, resilient)")
#     print("=" * 80)
    
#     # Create enhanced builder
#     builder = LangGraphWorkflowBuilder(ba_enhanced_path)
    
#     # Build and compile workflow
#     builder.build_workflow()
#     builder.compile()
    
#     print(f"\n[SUCCESS] Workflow ready!")
#     print(f"\n[EXEC] Executing workflow...\n")
    
#     # Execute workflow
#     result = builder.execute(initial_input)
    
#     # Save result
#     output_file = builder.save_result(result)
    
#     # Display result summary
#     if result['success']:
#         print(f"\n[SUCCESS] WORKFLOW COMPLETED SUCCESSFULLY!")
#         print(f"\n[SUMMARY] Summary:")
#         print(f"   Duration: {result['duration_seconds']:.2f}s")
#         print(f"   Agents executed: {result['agents_executed']}/{result['total_agents']}")
#         print(f"   Success rate: {result['agents_succeeded']}/{result['agents_executed']}")
#         if result.get('errors'):
#             print(f"   Errors: {len(result['errors'])}")
#         print(f"\n[SUCCESS] Full results saved to: {output_file}")
#     else:
#         print(f"\n[ERROR] WORKFLOW FAILED")
#         print(f"   Error: {result.get('error', 'Unknown')}")
#         print(f"   Duration before failure: {result['duration_seconds']:.2f}s")
#         print(f"\n[ERROR] Error details saved to: {output_file}")


# if __name__ == "__main__":
#     MODULE_NAME = "langgraph_workflow_builder"
#     start_time = time.time()

#     main()

#     duration = time.time() - start_time
#     print(f"\n[TIMING] {MODULE_NAME}: {duration:.2f}s")

#     try:
#         import json
#         timing_entry = {
#             "module": MODULE_NAME,
#             "duration_seconds": round(duration, 2),
#             "timestamp": datetime.now().isoformat()
#         }
#         with open('timing_log.jsonl', 'a', encoding='utf-8') as f:
#             f.write(json.dumps(timing_entry) + '\n')
#     except Exception as e:
#         print(f"[WARNING] Could not save timing: {e}")


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MetaFlow Enhanced Workflow Builder
Orchestrates multi-agent workflows with robust error handling and monitoring
"""

import json
import time
import logging
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import importlib.util
import sys

from langgraph.graph import StateGraph, END

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnhancedWorkflowBuilder:
    """
    Enhanced workflow builder with comprehensive error handling,
    retry logic, and monitoring capabilities
    """
    
    def __init__(
        self,
        workflow_config_path: str,
        lm_studio_url: str = "http://localhost:1234/v1",
        lm_studio_model: str = "qwen2.5-coder-14b-instruct",
        max_agent_retries: int = 2
    ):
        self.workflow_config_path = workflow_config_path
        self.lm_studio_url = lm_studio_url
        self.lm_studio_model = lm_studio_model
        self.max_agent_retries = max_agent_retries
        
        self.workflow_config = None
        self.agents = {}
        self.workflow_graph = None
        self.compiled_workflow = None
        
        # Import agent factory dynamically
        self.agent_factory_module = self._import_agent_factory()
        
    def _import_agent_factory(self):
        """Dynamically import the best available agent factory"""
        factory_options = [
            'langchain_agentfactory_functional',
            'langchain_agentfactory_minimal',
            'langchain_agentfactory_original',
            'langchain_agentfactory'
        ]
        
        base_path = Path(__file__).parent
        
        for factory_name in factory_options:
            factory_path = base_path / f"{factory_name}.py"
            
            if factory_path.exists():
                try:
                    spec = importlib.util.spec_from_file_location(factory_name, factory_path)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[factory_name] = module
                    spec.loader.exec_module(module)
                    
                    logger.info(f"[INFO] Imported agent factory from: {factory_name}.py")
                    return module
                    
                except Exception as e:
                    logger.warning(f"[WARN] Could not import {factory_name}: {e}")
                    continue
        
        raise ImportError("No agent factory module found!")
    
    def load_workflow(self):
        """Load workflow configuration from JSON file"""
        logger.info(f"[INFO] Loading workflow configuration from: {self.workflow_config_path}")
        
        with open(self.workflow_config_path, 'r', encoding='utf-8') as f:
            self.workflow_config = json.load(f)
        
        logger.info("[INFO] Workflow configuration loaded successfully")
    
    def initialize_agents(self):
        """Initialize all agents using the agent factory"""
        logger.info("[INFO] Initializing Enhanced Agent Factory...")
        
        factory_class = self.agent_factory_module.LangChainAgentFactory
        
        factory = factory_class(
            lm_studio_url=self.lm_studio_url,
            lm_studio_model=self.lm_studio_model,
            enable_pruning=True,
            enable_qc=True
        )
        
        logger.info(f"[INFO] Creating {len(self.workflow_config['agents'])} agents...")
        
        # Create agents with pruning and QC
        self.agents, metadata = factory.create_all_agents(self.workflow_config_path)
        
        # Check if pruning reduced agent count
        if 'pruning' in metadata and metadata['pruning']['pruned_count'] > 0:
            logger.info(f"[INFO] Pruning detected ({len(self.agents)} agents). Reloading workflow from: BA_enhanced_pruned.json")
            
            # Reload workflow config from pruned version
            pruned_path = self.workflow_config_path.replace('.json', '_pruned.json')
            if Path(pruned_path).exists():
                with open(pruned_path, 'r', encoding='utf-8') as f:
                    self.workflow_config = json.load(f)
                logger.info(f"[INFO] Workflow updated. New agent count: {len(self.workflow_config['agents'])}")
        
        logger.info("[SUCCESS] Workflow Builder initialized")
        
        # Safe field access with .get()
        workflow_metadata = self.workflow_config.get('workflow_metadata', {})
        orchestration = self.workflow_config.get('orchestration', {})
        
        workflow_id = workflow_metadata.get('id') or workflow_metadata.get('workflow_id') or 'unknown_id'
        domain = workflow_metadata.get('domain', 'unknown')
        pattern = orchestration.get('pattern', 'unknown')
        
        logger.info(f"   Workflow ID: {workflow_id}")
        logger.info(f"   Domain: {domain}")
        logger.info(f"   Architecture: {pattern}")
        logger.info(f"   Total agents: {len(self.agents)}")
        logger.info(f"   Max retries per agent: {self.max_agent_retries}")
    
    def build_workflow(self):
        """Build the workflow graph based on orchestration pattern"""
        logger.info("[INFO] Building workflow graph...")
        
        pattern = self.workflow_config.get('orchestration', {}).get('pattern', 'Pipeline/Sequential')
        logger.info(f"   Pattern: {pattern}")
        
        if pattern == "Pipeline/Sequential":
            workflow = self._build_pipeline_workflow()
        elif pattern == "Hub-and-Spoke":
            workflow = self._build_hub_spoke_workflow()
        elif pattern == "Hierarchical":
            workflow = self._build_hierarchical_workflow()
        else:
            raise ValueError(f"Unknown orchestration pattern: {pattern}")
        
        logger.info("[SUCCESS] Workflow graph built successfully")
        
        # Compile the workflow
        logger.info("[INFO] Compiling workflow...")
        self.compiled_workflow = workflow.compile()
        logger.info("[SUCCESS] Workflow compiled and ready to execute")
    
    def _build_pipeline_workflow(self):
        """Build a sequential pipeline workflow"""
        logger.info("   Building PIPELINE workflow...")
        
        workflow = StateGraph(dict)
        
        # Sort agents by position
        sorted_agents = sorted(
            self.workflow_config['agents'],
            key=lambda a: a['position']
        )
        
        # Add nodes for each agent
        for agent_config in sorted_agents:
            agent_id = agent_config['agent_id']
            agent_name = agent_config['agent_name']
            
            # Create enhanced node with retry logic
            def create_node(aid=agent_id):
                def node(state):
                    state['agent_id'] = aid
                    return self.enhanced_agent_node(state)
                return node
            
            workflow.add_node(agent_id, create_node())
            logger.info(f"      Added node: {agent_name} (position {agent_config['position']})")
        
        # Add edges (sequential flow)
        if len(sorted_agents) > 0:
            # Set entry point
            first_agent_id = sorted_agents[0]['agent_id']
            workflow.set_entry_point(first_agent_id)
            logger.info(f"      Entry point: {first_agent_id}")
            
            # Connect sequential nodes
            for i in range(len(sorted_agents) - 1):
                current_id = sorted_agents[i]['agent_id']
                next_id = sorted_agents[i + 1]['agent_id']
                workflow.add_edge(current_id, next_id)
            
            # Set finish point
            last_agent_id = sorted_agents[-1]['agent_id']
            workflow.add_edge(last_agent_id, END)
            logger.info(f"      End point: {last_agent_id}")
        
        return workflow
    
    def _build_hub_spoke_workflow(self):
        """Build a hub-and-spoke workflow"""
        logger.info("   Building HUB-AND-SPOKE workflow...")
        
        workflow = StateGraph(dict)
        
        # Find hub agent (usually first or with most connections)
        hub_agent = self.workflow_config['agents'][0]
        hub_id = hub_agent['agent_id']
        
        # Add hub node
        def create_hub_node():
            def node(state):
                state['agent_id'] = hub_id
                return self.enhanced_agent_node(state)
            return node
        
        workflow.add_node(hub_id, create_hub_node())
        workflow.set_entry_point(hub_id)
        
        # Add spoke nodes
        for agent_config in self.workflow_config['agents'][1:]:
            agent_id = agent_config['agent_id']
            
            def create_spoke_node(aid=agent_id):
                def node(state):
                    state['agent_id'] = aid
                    return self.enhanced_agent_node(state)
                return node
            
            workflow.add_node(agent_id, create_spoke_node())
            
            # Connect hub to spoke
            workflow.add_edge(hub_id, agent_id)
            
            # Connect spoke back to hub or end
            workflow.add_edge(agent_id, END)
        
        return workflow
    
    def _build_hierarchical_workflow(self):
        """Build a hierarchical workflow"""
        logger.info("   Building HIERARCHICAL workflow...")
        
        workflow = StateGraph(dict)
        
        # Group agents by hierarchy level (using position as proxy)
        levels = {}
        for agent_config in self.workflow_config['agents']:
            position = agent_config['position']
            if position not in levels:
                levels[position] = []
            levels[position].append(agent_config)
        
        # Add nodes for all agents
        for agent_config in self.workflow_config['agents']:
            agent_id = agent_config['agent_id']
            
            def create_node(aid=agent_id):
                def node(state):
                    state['agent_id'] = aid
                    return self.enhanced_agent_node(state)
                return node
            
            workflow.add_node(agent_id, create_node())
        
        # Set entry point (lowest position)
        min_position = min(levels.keys())
        entry_agent = levels[min_position][0]['agent_id']
        workflow.set_entry_point(entry_agent)
        
        # Connect levels
        sorted_positions = sorted(levels.keys())
        for i in range(len(sorted_positions) - 1):
            current_level = levels[sorted_positions[i]]
            next_level = levels[sorted_positions[i + 1]]
            
            # Connect each agent in current level to agents in next level
            for current_agent in current_level:
                for next_agent in next_level:
                    workflow.add_edge(current_agent['agent_id'], next_agent['agent_id'])
        
        # Connect last level to END
        max_position = max(levels.keys())
        for agent in levels[max_position]:
            workflow.add_edge(agent['agent_id'], END)
        
        return workflow
    
    def enhanced_agent_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced agent execution node with comprehensive error handling and retry logic
        """
        # Extract agent info
        agent_id = state.get('agent_id')
        if not agent_id:
            raise ValueError("agent_id not found in state")
        
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent_name = agent.metadata.get('agent_name', agent_id)
        agent_position = agent.metadata.get('position', '?')
        error_strategy = agent.metadata.get('error_strategy', 'retry')
        
        logger.info("\n" + "="*60)
        logger.info("[INFO] Starting Agent Execution")
        logger.info(f"   Agent: {agent_name}")
        logger.info(f"   Position: {agent_position}")
        logger.info(f"   Error Strategy: {error_strategy}")
        logger.info("="*60)
        
        # Determine input source
        if 'agent_outputs' in state and state['agent_outputs']:
            input_source = "Previous agent output"
        else:
            input_source = "Initial workflow input"
        
        logger.info(f"   Input Source: {input_source}")
        logger.info(f"   Input Preview: {str(state.get('input', ''))[:100]}...")
        
        # ═══════════════════════════════════════════════════════════════════════
        # EXECUTE AGENT WITH PROPER INPUT (CRITICAL SECTION - FIXED)
        # ═══════════════════════════════════════════════════════════════════════
        
        for attempt in range(self.max_agent_retries + 1):
            try:
                logger.info(f"   [EXEC] Executing agent...")
                
                start_time = time.time()
                
                # Ensure input is string, not dict
                agent_input = state.get('input', '')
                
                # If input is a dict, convert to string description
                if isinstance(agent_input, dict):
                    if 'input' in agent_input:
                        agent_input = agent_input['input']
                    elif 'task' in agent_input:
                        agent_input = agent_input['task']
                    elif 'description' in agent_input:
                        agent_input = agent_input['description']
                    elif 'prompt' in agent_input:
                        agent_input = agent_input['prompt']
                    else:
                        agent_input = f"Execute workflow with parameters: {', '.join(agent_input.keys())}"
                
                # Ensure it's a string
                if not isinstance(agent_input, str):
                    agent_input = str(agent_input)
                
                result = agent.invoke({
                    'input': agent_input,  # Now guaranteed to be string
                    'chat_history': state.get('chat_history', '')
                })
                
                duration = time.time() - start_time
                
                # Extract output
                output = result.get('output', '')
                token_stats = result.get('token_stats', {})
                
                logger.info(f"   [SUCCESS] Agent completed successfully")
                logger.info(f"   [TIME] Duration: {duration:.2f} seconds")
                logger.info(f"   [OUT] Output Preview: {str(output)[:100]}...")
                logger.info("="*60 + "\n")
                
                # Update state
                if 'agent_outputs' not in state:
                    state['agent_outputs'] = {}
                
                state['agent_outputs'][agent_id] = {
                    'output': output,
                    'duration': duration,
                    'timestamp': datetime.now().isoformat(),
                    'token_stats': token_stats
                }
                
                # Update execution log
                if 'execution_log' not in state:
                    state['execution_log'] = []
                
                state['execution_log'].append({
                    'agent_id': agent_id,
                    'agent_name': agent_name,
                    'position': agent_position,
                    'start_time': datetime.fromtimestamp(start_time).isoformat(),
                    'end_time': datetime.now().isoformat(),
                    'duration': duration,
                    'status': 'success',
                    'output_length': len(str(output)),
                    'retry_count': attempt,
                    'token_stats': token_stats
                })
                
                # Update input for next agent
                state['input'] = output
                state['chat_history'] = f"{state.get('chat_history', '')}\nAgent {agent_name}: {output}"
                
                return state
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"   [ERROR] Agent execution failed: {error_msg}")
                
                if attempt < self.max_agent_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"   [WAIT] Will retry in {wait_time}s...")
                    logger.info(f"   [RETRY] Retry attempt {attempt + 1}/{self.max_agent_retries}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"   [ERROR] All retry attempts exhausted")
                    
                    # Handle based on error strategy
                    if error_strategy == "skip":
                        logger.warning(f"   [SKIP] Error strategy: SKIP - Continuing workflow")
                        
                        # Log the skip
                        if 'execution_log' not in state:
                            state['execution_log'] = []
                        
                        state['execution_log'].append({
                            'agent_id': agent_id,
                            'agent_name': agent_name,
                            'position': agent_position,
                            'start_time': datetime.now().isoformat(),
                            'end_time': datetime.now().isoformat(),
                            'duration': 0,
                            'status': 'skipped',
                            'error': error_msg,
                            'retry_count': self.max_agent_retries
                        })
                        
                        # Continue with placeholder output
                        state['input'] = f"[Agent {agent_name} skipped due to error: {error_msg}]"
                        return state
                    
                    else:  # fail or retry
                        logger.error(f"   [STOP] Error strategy: {error_strategy.upper()} - All retries exhausted, failing")
                        raise Exception(f"Agent {agent_name} failed after {self.max_agent_retries} retries: {error_msg}")
        
        # Should never reach here
        raise Exception(f"Agent {agent_name} execution failed unexpectedly")
    
    def execute(self, user_input: str = None):
        """
        Execute the compiled workflow
        
        Args:
            user_input: Optional explicit user task. If not provided, will be extracted from workflow config.
        """
        if not self.compiled_workflow:
            raise Exception("Workflow not compiled. Call build_workflow() first.")
        
        # Safe field access
        workflow_metadata = self.workflow_config.get('workflow_metadata', {})
        orchestration = self.workflow_config.get('orchestration', {})
        
        workflow_id = workflow_metadata.get('workflow_id') or workflow_metadata.get('id') or 'unknown_id'
        domain = workflow_metadata.get('domain', 'unknown')
        pattern = orchestration.get('pattern', 'unknown')
        
        logger.info("\n" + "="*80)
        logger.info("[START] STARTING WORKFLOW EXECUTION")
        logger.info("="*80)
        logger.info(f"Workflow ID: {workflow_id}")
        logger.info(f"Domain: {domain}")
        logger.info(f"Architecture: {pattern}")
        logger.info(f"Total Agents: {len(self.workflow_config.get('agents', []))}")
        logger.info("="*80 + "\n")
        
        # Extract actual user task with multiple fallback strategies
        user_task = user_input  # Explicit input takes priority
        
        # Strategy 1: Get from workflow_metadata.user_prompt (ADDED BY BASE_AGENT_4)
        if not user_task:
            user_task = workflow_metadata.get('user_prompt')
            if user_task:
                logger.info(f"[TASK] Loaded user prompt from workflow metadata")
        
        # Strategy 2: Check other metadata fields
        if not user_task:
            user_task = (
                workflow_metadata.get('task') or 
                workflow_metadata.get('description') or
                workflow_metadata.get('objective')
            )
        
        # Strategy 3: Use first agent's description
        if not user_task:
            agents = self.workflow_config.get('agents', [])
            if agents:
                first_agent = agents[0]
                identity = first_agent.get('identity', {})
                user_task = identity.get('description') or identity.get('role')
        
        # Strategy 4: Construct from all agent roles
        if not user_task:
            agent_roles = []
            for agent in self.workflow_config.get('agents', []):
                role = agent.get('identity', {}).get('role', '')
                if role:
                    agent_roles.append(role)
            
            if agent_roles:
                user_task = f"Execute workflow with the following roles: {', '.join(agent_roles)}"
        
        # Strategy 5: Generic fallback
        if not user_task:
            user_task = "Execute the assigned workflow tasks using available tools to achieve the workflow objectives"
        
        logger.info(f"[EXEC] Executing workflow...")
        logger.info(f"[TASK] User Task: {user_task}\n")
        
        # ═══════════════════════════════════════════════════════════════════════
        # CREATE INITIAL STATE WITH ACTUAL TASK (CRITICAL FIX)
        # ═══════════════════════════════════════════════════════════════════════
        
        # Create initial state with actual task
        initial_state = {
            'input': user_task,  # CRITICAL FIX - Pass actual user task
            'chat_history': '',
            'workflow_id': workflow_id,
            'execution_start': datetime.now().isoformat(),
            'agent_outputs': {},
            'execution_log': []
        }
        
        # ═══════════════════════════════════════════════════════════════════════
        # EXECUTE WORKFLOW
        # ═══════════════════════════════════════════════════════════════════════
        
        start_time = time.time()
        
        try:
            logger.info("[EXEC] Executing workflow...")
            final_state = self.compiled_workflow.invoke(initial_state)
            
            duration = time.time() - start_time
            
            logger.info("\n" + "="*80)
            logger.info("[SUCCESS] WORKFLOW COMPLETED SUCCESSFULLY")
            logger.info("="*80)
            logger.info(f"[TIME] Total Duration: {duration:.2f} seconds")
            logger.info("="*80 + "\n")
            
            # Build result
            result = self._build_success_result(final_state, duration)
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            
            logger.error("\n" + "="*80)
            logger.error("[ERROR] WORKFLOW FAILED")
            logger.error("="*80)
            logger.error(f"Error: {error_msg}")
            logger.error(f"[TIME] Duration before failure: {duration:.2f} seconds")
            logger.error("="*80 + "\n")
            
            # Log full traceback
            logger.error("Traceback:")
            logger.error(traceback.format_exc())
            
            # Build error result
            result = self._build_error_result(initial_state, error_msg, duration)
            
            return result
    
    def _build_success_result(self, final_state: Dict[str, Any], duration: float) -> Dict[str, Any]:
        """Build success result dictionary"""
        
        execution_log = final_state.get('execution_log', [])
        agent_outputs = final_state.get('agent_outputs', {})
        
        # Count successes/failures
        agents_executed = len(execution_log)
        agents_succeeded = sum(1 for log in execution_log if log.get('status') == 'success')
        agents_failed = agents_executed - agents_succeeded
        
        # Get final output
        if agent_outputs:
            last_agent_id = list(agent_outputs.keys())[-1]
            final_output = agent_outputs[last_agent_id].get('output', '')
        else:
            final_output = final_state.get('input', '')
        
        workflow_metadata = self.workflow_config.get('workflow_metadata', {})
        orchestration = self.workflow_config.get('orchestration', {})
        
        workflow_id = workflow_metadata.get('workflow_id') or workflow_metadata.get('id') or 'unknown_id'
        domain = workflow_metadata.get('domain', 'unknown')
        pattern = orchestration.get('pattern', 'unknown')
        
        result = {
            'success': True,
            'workflow_id': workflow_id,
            'domain': domain,
            'architecture': pattern,
            'duration_seconds': round(duration, 5),
            'start_time': final_state.get('execution_start'),
            'end_time': datetime.now().isoformat(),
            'total_agents': len(self.workflow_config['agents']),
            'agents_executed': agents_executed,
            'agents_succeeded': agents_succeeded,
            'agents_failed': agents_failed,
            'final_output': final_output,
            'agent_outputs': agent_outputs,
            'execution_log': execution_log,
            'errors': [],
            'retry_counts': {}
        }
        
        # Extract retry counts
        for log in execution_log:
            if log.get('retry_count', 0) > 0:
                result['retry_counts'][log['agent_id']] = log['retry_count']
        
        return result
    
    def _build_error_result(self, initial_state: Dict[str, Any], error_msg: str, duration: float) -> Dict[str, Any]:
        """Build error result dictionary"""
        
        execution_log = initial_state.get('execution_log', [])
        agent_outputs = initial_state.get('agent_outputs', {})
        
        agents_executed = len(execution_log)
        agents_succeeded = sum(1 for log in execution_log if log.get('status') == 'success')
        agents_failed = agents_executed - agents_succeeded
        
        workflow_metadata = self.workflow_config.get('workflow_metadata', {})
        orchestration = self.workflow_config.get('orchestration', {})
        
        workflow_id = workflow_metadata.get('workflow_id') or workflow_metadata.get('id') or 'unknown_id'
        domain = workflow_metadata.get('domain', 'unknown')
        pattern = orchestration.get('pattern', 'unknown')
        
        result = {
            'success': False,
            'workflow_id': workflow_id,
            'domain': domain,
            'architecture': pattern,
            'duration_seconds': round(duration, 5),
            'start_time': initial_state.get('execution_start'),
            'end_time': datetime.now().isoformat(),
            'total_agents': len(self.workflow_config['agents']),
            'agents_executed': agents_executed,
            'agents_succeeded': agents_succeeded,
            'agents_failed': agents_failed,
            'final_output': None,
            'agent_outputs': agent_outputs,
            'execution_log': execution_log,
            'errors': [error_msg],
            'retry_counts': {}
        }
        
        return result
    
    def save_result(self, result: Dict[str, Any]) -> str:
        """Save workflow execution result to JSON file"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"workflow_result_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"[SUCCESS] Result saved to: {filename}")
        
        return filename
    
    def print_summary(self, result: Dict[str, Any]):
        """Print execution summary"""
        
        logger.info("\n" + "="*80)
        logger.info("[SUMMARY] WORKFLOW EXECUTION SUMMARY")
        logger.info("="*80)
        logger.info(f"Workflow ID: {result['workflow_id']}")
        logger.info(f"Domain: {result['domain']}")
        logger.info(f"Architecture: {result['architecture']}")
        logger.info("\n[METRICS] PERFORMANCE METRICS:")
        logger.info(f"   Total Duration: {result['duration_seconds']} seconds")
        logger.info(f"   Agents Total: {result['total_agents']}")
        logger.info(f"   Agents Executed: {result['agents_executed']}")
        logger.info(f"   Agents Succeeded: {result['agents_succeeded']}")
        logger.info(f"   Agents Failed: {result['agents_failed']}")
        
        logger.info("\n[TIMELINE] EXECUTION TIMELINE:")
        for log in result.get('execution_log', []):
            status_icon = "[OK]" if log['status'] == 'success' else "[FAIL]"
            logger.info(f"   {status_icon} {log.get('position', '?')}. {log['agent_name']}")
            logger.info(f"      Duration: {log['duration']:.2f}s")
        
        logger.info("="*80 + "\n")


def main():
    """Main execution function"""
    import sys
    
    # Print header
    print("\n[INFO] MetaFlow Enhanced Workflow Builder")
    print("="*80)
    
    # Check arguments
    if len(sys.argv) < 2:
        print("[ERROR] Usage: python langgraph_workflow_builder.py <BA_enhanced.json> [user_task]")
        sys.exit(1)
    
    workflow_file = sys.argv[1]
    user_task = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"[INFO] Workflow: {workflow_file}")
    print(f"[INFO] LLM: Qwen 2.5 14B (local)")
    print(f"[INFO] Tools: MCP via Claude Code")
    print(f"[INFO] Mode: Enhanced (validated, monitored, resilient)")
    print("="*80 + "\n")
    
    # Add timing tracking
    MODULE_NAME = "langgraph_workflow_builder"
    start_time = time.time()
    
    try:
        # Initialize builder
        builder = EnhancedWorkflowBuilder(
            workflow_config_path=workflow_file,
            max_agent_retries=2
        )
        
        # Load workflow
        builder.load_workflow()
        
        # Initialize agents
        builder.initialize_agents()
        
        # Build workflow
        builder.build_workflow()
        
        print("\n[SUCCESS] Workflow ready!\n")
        print("[EXEC] Executing workflow...\n")
        
        # Execute workflow
        result = builder.execute(user_input=user_task)
        
        # Save result
        result_file = builder.save_result(result)
        
        # Print summary
        builder.print_summary(result)
        
        # Print final status
        if result['success']:
            print("\n[SUCCESS] WORKFLOW COMPLETED SUCCESSFULLY!\n")
            print(f"[SUMMARY] Summary:")
            print(f"   Duration: {result['duration_seconds']:.2f}s")
            print(f"   Agents executed: {result['agents_executed']}/{result['total_agents']}")
            print(f"   Success rate: {result['agents_succeeded']}/{result['agents_executed']}\n")
            print(f"[SUCCESS] Full results saved to: {result_file}\n")
        else:
            print("\n[ERROR] WORKFLOW FAILED\n")
            print(f"   Error: {result['errors'][0]}")
            print(f"   Duration before failure: {result['duration_seconds']:.2f}s\n")
            print(f"[ERROR] Error details saved to: {result_file}\n")
        
    except Exception as e:
        print(f"\n[ERROR] Fatal error: {e}\n")
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        # Add timing at the end
        duration = time.time() - start_time
        print(f"[TIMING] {MODULE_NAME}: {duration:.2f}s")
        
        # Save timing log
        try:
            timing_entry = {
                "module": MODULE_NAME,
                "duration_seconds": round(duration, 2),
                "timestamp": datetime.now().isoformat()
            }
            with open('timing_log.jsonl', 'a', encoding='utf-8') as f:
                f.write(json.dumps(timing_entry) + '\n')
        except Exception as e:
            print(f"[WARNING] Could not save timing: {e}")


if __name__ == "__main__":
    main()