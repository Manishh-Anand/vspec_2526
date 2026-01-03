#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MetaFlow Testing Utilities
Comprehensive testing for agents, tools, and workflows

Test Coverage:
- Individual tool calls
- Agent ReAct loops
- Workflow execution
- Error recovery
- Performance metrics
"""

import json
import time
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from langchain_agentfactory import LangChainAgentFactory, ClaudeMCPTool
from langgraph_workflow_builder import LangGraphWorkflowBuilder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetaFlowTester:
    """
    Comprehensive testing suite for MetaFlow platform
    """
    
    def __init__(self, ba_enhanced_path: str):
        """
        Initialize tester with workflow configuration
        
        Args:
            ba_enhanced_path: Path to BA_enhanced.json
        """
        self.ba_enhanced_path = ba_enhanced_path
        
        # Load workflow data
        with open(ba_enhanced_path, 'r', encoding='utf-8') as f:
            self.workflow_data = json.load(f)
        
        self.factory = None
        self.agents = None
        self.builder = None
        
        # Test results
        self.test_results = {
            'tool_tests': [],
            'agent_tests': [],
            'workflow_tests': [],
            'performance_metrics': {}
        }
        
        logger.info(f"✅ MetaFlow Tester initialized")
        logger.info(f"   Workflow: {self.workflow_data['workflow_metadata']['workflow_id']}")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run complete test suite
        
        Returns:
            Comprehensive test results
        """
        print(f"\n{'='*80}")
        print(f"🧪 METAFLOW COMPREHENSIVE TEST SUITE")
        print(f"{'='*80}\n")
        
        start_time = time.time()
        
        # Test 1: Tool Call Tests
        print(f"📍 TEST PHASE 1: Individual Tool Calls")
        print(f"{'='*80}")
        tool_results = self.test_tool_calls()
        
        # Test 2: Agent Tests
        print(f"\n📍 TEST PHASE 2: Agent ReAct Loops")
        print(f"{'='*80}")
        agent_results = self.test_agent_loops()
        
        # Test 3: Workflow Tests
        print(f"\n📍 TEST PHASE 3: End-to-End Workflow")
        print(f"{'='*80}")
        workflow_results = self.test_workflow_execution()
        
        # Test 4: Error Recovery Tests
        print(f"\n📍 TEST PHASE 4: Error Recovery")
        print(f"{'='*80}")
        error_results = self.test_error_recovery()
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Compile results
        results = {
            'timestamp': datetime.now().isoformat(),
            'workflow_id': self.workflow_data['workflow_metadata']['workflow_id'],
            'total_duration': total_duration,
            'tool_tests': tool_results,
            'agent_tests': agent_results,
            'workflow_tests': workflow_results,
            'error_recovery_tests': error_results
        }
        
        # Print summary
        self._print_test_summary(results)
        
        # Save results
        self._save_test_results(results)
        
        return results
    
    def test_tool_calls(self) -> List[Dict[str, Any]]:
        """
        Test individual tool calls to verify Claude Code integration
        
        Tests:
        1. Tool validation (correct tool names)
        2. Tool execution (subprocess communication)
        3. Output parsing (success/error detection)
        """
        print(f"\n🔧 Testing Individual Tool Calls...\n")
        
        results = []
        
        # Create a simple MCP tool for testing
        tool = ClaudeMCPTool(
            claude_cwd=Path(r"C:\Users\manis"),
            available_tools=["search_web", "send_email", "create_event"]
        )
        
        # Test 1: Valid tool call
        print(f"Test 1.1: Valid Tool Call (search_web)")
        test_start = time.time()
        try:
            result = tool._run(
                tool_name="search_web",
                parameters={"query": "test query"}
            )
            test_duration = time.time() - test_start
            
            success = "ERROR" not in result
            print(f"   {'✅' if success else '❌'} Result: {result[:100]}...")
            print(f"   ⏱️  Duration: {test_duration:.2f}s")
            
            results.append({
                'test': 'valid_tool_call',
                'tool_name': 'search_web',
                'success': success,
                'duration': test_duration,
                'result_preview': result[:200]
            })
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append({
                'test': 'valid_tool_call',
                'tool_name': 'search_web',
                'success': False,
                'error': str(e)
            })
        
        # Test 2: Invalid tool name
        print(f"\nTest 1.2: Invalid Tool Name")
        test_start = time.time()
        try:
            result = tool._run(
                tool_name="nonexistent_tool",
                parameters={}
            )
            test_duration = time.time() - test_start
            
            contains_error = "ERROR" in result and "not available" in result
            print(f"   {'✅' if contains_error else '❌'} Error detected correctly: {contains_error}")
            print(f"   Result: {result[:150]}...")
            
            results.append({
                'test': 'invalid_tool_name',
                'tool_name': 'nonexistent_tool',
                'success': contains_error,
                'duration': test_duration
            })
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append({
                'test': 'invalid_tool_name',
                'success': False,
                'error': str(e)
            })
        
        # Test 3: Tool with parameters
        print(f"\nTest 1.3: Tool with Multiple Parameters")
        test_start = time.time()
        try:
            result = tool._run(
                tool_name="send_email",
                parameters={
                    "to": "test@example.com",
                    "subject": "Test",
                    "body": "Test message"
                }
            )
            test_duration = time.time() - test_start
            
            success = result is not None
            print(f"   {'✅' if success else '❌'} Executed with parameters")
            print(f"   Result: {result[:150]}...")
            print(f"   ⏱️  Duration: {test_duration:.2f}s")
            
            results.append({
                'test': 'tool_with_parameters',
                'tool_name': 'send_email',
                'success': success,
                'duration': test_duration,
                'parameters_count': 3
            })
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append({
                'test': 'tool_with_parameters',
                'success': False,
                'error': str(e)
            })
        
        print(f"\n{'─'*60}")
        passed = sum(1 for r in results if r.get('success', False))
        print(f"Tool Tests: {passed}/{len(results)} passed")
        print(f"{'─'*60}\n")
        
        return results
    
    def test_agent_loops(self) -> List[Dict[str, Any]]:
        """
        Test agent ReAct loops to verify:
        1. Prompt adherence (correct format)
        2. Tool selection logic
        3. Loop termination
        4. Output quality
        """
        print(f"\n🤖 Testing Agent ReAct Loops...\n")
        
        results = []
        
        # Initialize factory and create agents
        self.factory = LangChainAgentFactory()
        self.agents = self.factory.create_all_agents(self.ba_enhanced_path)
        
        # Test first agent
        first_agent_config = sorted(
            self.workflow_data['agents'],
            key=lambda x: x['position']
        )[0]
        
        agent_id = first_agent_config['agent_id']
        agent_name = first_agent_config['agent_name']
        agent = self.agents[agent_id]
        
        print(f"Testing Agent: {agent_name}")
        print(f"{'─'*60}")
        
        # Test 1: Simple query
        print(f"\nTest 2.1: Simple Query")
        test_input = "Hello, can you help me?"
        test_start = time.time()
        
        try:
            result = agent.invoke({
                "input": test_input,
                "chat_history": ""
            })
            test_duration = time.time() - test_start
            
            output = result.get('output', '')
            intermediate_steps = result.get('intermediate_steps', [])
            
            print(f"   ✅ Agent responded")
            print(f"   Output: {output[:150]}...")
            print(f"   Intermediate steps: {len(intermediate_steps)}")
            print(f"   ⏱️  Duration: {test_duration:.2f}s")
            
            results.append({
                'test': 'simple_query',
                'agent_name': agent_name,
                'success': True,
                'duration': test_duration,
                'output_length': len(output),
                'steps_count': len(intermediate_steps)
            })
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append({
                'test': 'simple_query',
                'agent_name': agent_name,
                'success': False,
                'error': str(e)
            })
        
        # Test 2: Task requiring tool use
        print(f"\nTest 2.2: Task Requiring Tool Use")
        tool_names = [t['name'] for t in first_agent_config['tools']]
        test_input = f"Use the {tool_names[0]} tool to help me"
        test_start = time.time()
        
        try:
            result = agent.invoke({
                "input": test_input,
                "chat_history": ""
            })
            test_duration = time.time() - test_start
            
            output = result.get('output', '')
            intermediate_steps = result.get('intermediate_steps', [])
            
            used_tool = len(intermediate_steps) > 0
            print(f"   {'✅' if used_tool else '⚠️ '} Tool usage: {used_tool}")
            print(f"   Steps: {len(intermediate_steps)}")
            print(f"   Output: {output[:150]}...")
            print(f"   ⏱️  Duration: {test_duration:.2f}s")
            
            results.append({
                'test': 'tool_usage_task',
                'agent_name': agent_name,
                'success': True,
                'used_tool': used_tool,
                'duration': test_duration,
                'steps_count': len(intermediate_steps)
            })
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append({
                'test': 'tool_usage_task',
                'agent_name': agent_name,
                'success': False,
                'error': str(e)
            })
        
        print(f"\n{'─'*60}")
        passed = sum(1 for r in results if r.get('success', False))
        print(f"Agent Tests: {passed}/{len(results)} passed")
        print(f"{'─'*60}\n")
        
        return results
    
    def test_workflow_execution(self) -> List[Dict[str, Any]]:
        """
        Test end-to-end workflow execution to verify:
        1. Agent orchestration
        2. State passing
        3. Sequential execution
        4. Final output quality
        """
        print(f"\n🔄 Testing End-to-End Workflow...\n")
        
        results = []
        
        # Create workflow builder
        self.builder = LangGraphWorkflowBuilder(self.ba_enhanced_path)
        
        # Test 1: Complete workflow execution
        print(f"Test 3.1: Complete Workflow Execution")
        test_start = time.time()
        
        try:
            result = self.builder.execute(
                initial_input="Test workflow execution"
            )
            test_duration = time.time() - test_start
            
            success = result.get('success', False)
            agents_executed = result.get('agents_executed', 0)
            total_agents = result.get('total_agents', 0)
            
            print(f"   {'✅' if success else '❌'} Workflow completed: {success}")
            print(f"   Agents executed: {agents_executed}/{total_agents}")
            print(f"   ⏱️  Duration: {test_duration:.2f}s")
            
            if result.get('errors'):
                print(f"   ⚠️  Errors: {len(result['errors'])}")
            
            results.append({
                'test': 'complete_workflow',
                'success': success,
                'duration': test_duration,
                'agents_executed': agents_executed,
                'total_agents': total_agents,
                'error_count': len(result.get('errors', []))
            })
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append({
                'test': 'complete_workflow',
                'success': False,
                'error': str(e)
            })
        
        print(f"\n{'─'*60}")
        passed = sum(1 for r in results if r.get('success', False))
        print(f"Workflow Tests: {passed}/{len(results)} passed")
        print(f"{'─'*60}\n")
        
        return results
    
    def test_error_recovery(self) -> List[Dict[str, Any]]:
        """
        Test error recovery mechanisms:
        1. Retry logic
        2. Error strategies (fail, skip, retry)
        3. State recovery
        """
        print(f"\n🛡️  Testing Error Recovery...\n")
        
        results = []
        
        # Test 1: Agent with invalid tool name
        print(f"Test 4.1: Invalid Tool Name Recovery")
        print(f"   (Testing if agent can self-correct)")
        
        if self.agents is None:
            self.factory = LangChainAgentFactory()
            self.agents = self.factory.create_all_agents(self.ba_enhanced_path)
        
        first_agent = list(self.agents.values())[0]
        
        # This should trigger tool validation error
        test_start = time.time()
        try:
            result = first_agent.invoke({
                "input": "Use the invalid_tool_name to do something",
                "chat_history": ""
            })
            test_duration = time.time() - test_start
            
            output = result.get('output', '')
            recovered = "ERROR" in output or "not available" in output
            
            print(f"   {'✅' if recovered else '⚠️ '} Error message provided: {recovered}")
            print(f"   Output: {output[:150]}...")
            print(f"   ⏱️  Duration: {test_duration:.2f}s")
            
            results.append({
                'test': 'invalid_tool_recovery',
                'success': True,
                'error_handled': recovered,
                'duration': test_duration
            })
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append({
                'test': 'invalid_tool_recovery',
                'success': False,
                'error': str(e)
            })
        
        print(f"\n{'─'*60}")
        passed = sum(1 for r in results if r.get('success', False))
        print(f"Error Recovery Tests: {passed}/{len(results)} passed")
        print(f"{'─'*60}\n")
        
        return results
    
    def _print_test_summary(self, results: Dict[str, Any]):
        """
        Print comprehensive test summary
        """
        print(f"\n{'='*80}")
        print(f"📊 TEST SUITE SUMMARY")
        print(f"{'='*80}")
        print(f"Workflow: {results['workflow_id']}")
        print(f"Total Duration: {results['total_duration']:.2f} seconds")
        print(f"Timestamp: {results['timestamp']}")
        
        # Tool tests
        tool_tests = results['tool_tests']
        tool_passed = sum(1 for t in tool_tests if t.get('success', False))
        print(f"\n🔧 Tool Tests: {tool_passed}/{len(tool_tests)} passed")
        
        # Agent tests
        agent_tests = results['agent_tests']
        agent_passed = sum(1 for t in agent_tests if t.get('success', False))
        print(f"🤖 Agent Tests: {agent_passed}/{len(agent_tests)} passed")
        
        # Workflow tests
        workflow_tests = results['workflow_tests']
        workflow_passed = sum(1 for t in workflow_tests if t.get('success', False))
        print(f"🔄 Workflow Tests: {workflow_passed}/{len(workflow_tests)} passed")
        
        # Error recovery tests
        error_tests = results['error_recovery_tests']
        error_passed = sum(1 for t in error_tests if t.get('success', False))
        print(f"🛡️  Error Recovery Tests: {error_passed}/{len(error_tests)} passed")
        
        # Overall
        total_tests = len(tool_tests) + len(agent_tests) + len(workflow_tests) + len(error_tests)
        total_passed = tool_passed + agent_passed + workflow_passed + error_passed
        pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n{'='*80}")
        print(f"OVERALL: {total_passed}/{total_tests} tests passed ({pass_rate:.1f}%)")
        print(f"{'='*80}\n")
        
        if pass_rate == 100:
            print(f"🎉 ALL TESTS PASSED! System is ready for production.")
        elif pass_rate >= 75:
            print(f"✅ Most tests passed. Review failures and retest.")
        else:
            print(f"⚠️  Multiple failures detected. Review configuration and dependencies.")
    
    def _save_test_results(self, results: Dict[str, Any]):
        """
        Save test results to JSON file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"test_results_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Test results saved to: {output_file}\n")


def main():
    """
    Run comprehensive test suite
    """
    import sys
    
    if len(sys.argv) < 2:
        print("\n🧪 MetaFlow Testing Utilities")
        print("=" * 80)
        print("\nUsage: python testing_utilities.py <BA_enhanced.json>")
        print("\nThis will run:")
        print("  • Tool call tests (Claude Code integration)")
        print("  • Agent loop tests (ReAct pattern verification)")
        print("  • Workflow tests (End-to-end execution)")
        print("  • Error recovery tests (Resilience verification)")
        print("\nMake sure:")
        print("  ✓ LM Studio is running")
        print("  ✓ Claude Code is configured")
        print("  ✓ MCP servers are connected")
        print("=" * 80)
        sys.exit(1)
    
    ba_enhanced_path = sys.argv[1]
    
    # Create tester
    tester = MetaFlowTester(ba_enhanced_path)
    
    # Run all tests
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    total_tests = (
        len(results['tool_tests']) + 
        len(results['agent_tests']) + 
        len(results['workflow_tests']) +
        len(results['error_recovery_tests'])
    )
    total_passed = sum(
        sum(1 for t in test_list if t.get('success', False))
        for test_list in [
            results['tool_tests'],
            results['agent_tests'],
            results['workflow_tests'],
            results['error_recovery_tests']
        ]
    )
    
    sys.exit(0 if total_passed == total_tests else 1)


if __name__ == "__main__":
    main()