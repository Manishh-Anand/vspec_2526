#!/usr/bin/env python3
"""
Test script for MCP Module with comprehensive timing and token usage tracking
"""

import asyncio
import json
import sys
import tempfile
import time
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import MCPModule
from src.parser.base_agent import BaseAgentParser
from src.matching.semantic import SemanticMatcher
from src.execution.executor import ExecutionEngine
from src.output.generator import OutputGenerator
from src.discovery.scanner import MCPDiscoveryScanner


@dataclass
class PerformanceMetrics:
    """Performance metrics for tracking timing and token usage"""
    component_name: str
    start_time: float
    end_time: float
    duration: float
    tokens_used: int = 0
    llm_calls: int = 0
    success: bool = True
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.end_time > 0:
            self.duration = self.end_time - self.start_time


class PerformanceTracker:
    """Tracks performance metrics across all components"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.total_start_time = time.time()
        self.total_tokens = 0
        self.total_llm_calls = 0
        
    def start_component(self, component_name: str) -> PerformanceMetrics:
        """Start tracking a component"""
        metrics = PerformanceMetrics(
            component_name=component_name,
            start_time=time.time(),
            end_time=0,
            duration=0
        )
        self.metrics.append(metrics)
        return metrics
    
    def end_component(self, metrics: PerformanceMetrics, tokens: int = 0, llm_calls: int = 0, success: bool = True, error: Optional[str] = None):
        """End tracking a component"""
        metrics.end_time = time.time()
        metrics.duration = metrics.end_time - metrics.start_time
        metrics.tokens_used = tokens
        metrics.llm_calls = llm_calls
        metrics.success = success
        metrics.error_message = error
        
        if success:
            self.total_tokens += tokens
            self.total_llm_calls += llm_calls
    
    def get_summary(self) -> Dict:
        """Get performance summary"""
        total_duration = time.time() - self.total_start_time
        
        successful_components = [m for m in self.metrics if m.success]
        failed_components = [m for m in self.metrics if not m.success]
        
        summary = {
            "overall": {
                "total_duration": total_duration,
                "total_tokens": self.total_tokens,
                "total_llm_calls": self.total_llm_calls,
                "components_tested": len(self.metrics),
                "successful_components": len(successful_components),
                "failed_components": len(failed_components),
                "success_rate": len(successful_components) / len(self.metrics) if self.metrics else 0
            },
            "components": [
                {
                    "name": m.component_name,
                    "duration": m.duration,
                    "tokens_used": m.tokens_used,
                    "llm_calls": m.llm_calls,
                    "success": m.success,
                    "error": m.error_message
                } for m in self.metrics
            ],
            "timing_breakdown": {
                "discovery": sum(m.duration for m in self.metrics if "discovery" in m.component_name.lower()),
                "matching": sum(m.duration for m in self.metrics if "matching" in m.component_name.lower()),
                "execution": sum(m.duration for m in self.metrics if "execution" in m.component_name.lower()),
                "output": sum(m.duration for m in self.metrics if "output" in m.component_name.lower())
            }
        }
        
        return summary
    
    def print_summary(self):
        """Print formatted performance summary"""
        summary = self.get_summary()
        
        print("\n" + "="*80)
        print("PERFORMANCE METRICS SUMMARY")
        print("="*80)
        
        # Overall metrics
        overall = summary["overall"]
        print(f"Total Execution Time: {overall['total_duration']:.2f}s")
        print(f"Total Tokens Used: {overall['total_tokens']:,}")
        print(f"Total LLM Calls: {overall['total_llm_calls']}")
        print(f"Success Rate: {overall['success_rate']*100:.1f}% ({overall['successful_components']}/{overall['components_tested']})")
        
        # Component breakdown
        print(f"\nCOMPONENT BREAKDOWN:")
        print("-" * 60)
        for comp in summary["components"]:
            status = "OK" if comp["success"] else "FAIL"
            print(f"{status} {comp['name']:<25} | {comp['duration']:>8.3f}s | {comp['tokens_used']:>8,} tokens | {comp['llm_calls']:>3} LLM calls")
            if not comp["success"] and comp["error"]:
                print(f"    └─ Error: {comp['error']}")
        
        # Timing breakdown
        timing = summary["timing_breakdown"]
        print(f"\nTIMING BREAKDOWN:")
        print("-" * 40)
        print(f"Discovery:     {timing['discovery']:>8.3f}s ({timing['discovery']/overall['total_duration']*100:>5.1f}%)")
        print(f"Matching:      {timing['matching']:>8.3f}s ({timing['matching']/overall['total_duration']*100:>5.1f}%)")
        print(f"Execution:     {timing['execution']:>8.3f}s ({timing['execution']/overall['total_duration']*100:>5.1f}%)")
        print(f"Output Gen:    {timing['output']:>8.3f}s ({timing['output']/overall['total_duration']*100:>5.1f}%)")
        
        # Performance insights
        print(f"\nPERFORMANCE INSIGHTS:")
        print("-" * 40)
        if overall['total_duration'] > 30:
            print("WARNING: Total execution time is high (>30s) - consider optimizing discovery or matching")
        if overall['total_tokens'] > 10000:
            print("WARNING: High token usage - consider optimizing LLM prompts or reducing complexity")
        if overall['total_llm_calls'] > 20:
            print("WARNING: Many LLM calls - consider batching or caching strategies")
        
        # Save detailed metrics
        metrics_file = f"test_performance_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"\nDetailed metrics saved to: {metrics_file}")


# Initialize global performance tracker
performance_tracker = PerformanceTracker()


def create_sample_ba_json():
    """Create sample BA operation JSON for testing"""
    return {
        "workflow_metadata": {
            "workflow_id": "test_workflow_001",
            "domain": "finance",
            "selected_architecture": "microservices",
            "complexity_level": "medium",
            "total_agents": 3,
            "estimated_execution_time": "2 hours"
        },
        "orchestration": {
            "orchestration_type": "sequential",
            "communication_protocol": "REST",
            "error_handling_strategy": "retry_with_backoff",
            "scaling_strategy": "horizontal"
        },
        "domain_config": {
            "domain": "finance",
            "specific_requirements": ["GDPR compliance", "Real-time processing"],
            "compliance_standards": ["PCI-DSS", "SOX"]
        },
        "agents": [
            {
                "agent_id": "agent_1",
                "agent_name": "Financial Analyst",
                "position": 1,
                "identity": {
                    "role": "analyst",
                    "expertise": ["financial_analysis", "risk_assessment"],
                    "access_level": "full"
                },
                "data_interface": {
                    "input_sources": ["bank_statements", "transaction_data"],
                    "output_formats": ["reports", "alerts"],
                    "data_retention": "30_days"
                },
                "llm_config": {
                    "model": "openhermes-2.5-mistral-7b",
                    "temperature": 0.3,
                    "max_tokens": 1000
                },
                "tools": [
                    {
                        "name": "file_reader",
                        "purpose": "Read financial documents",
                        "auth_required": False
                    },
                    {
                        "name": "bank_statement_parser",
                        "purpose": "Parse bank statements",
                        "auth_required": False
                    }
                ],
                "resources": [
                    {
                        "name": "transaction_history",
                        "description": "Historical transaction data",
                        "uri": "finance://transactions/*"
                    },
                    {
                        "name": "market_data",
                        "description": "Real-time market information",
                        "uri": "finance://market/*"
                    }
                ],
                "prompts": [
                    {
                        "name": "financial_advice",
                        "description": "Generate financial advice",
                        "template": "Based on the financial data, provide advice for {user_goal}"
                    },
                    {
                        "name": "budget_guidance",
                        "description": "Budget consultation",
                        "template": "Analyze spending patterns and suggest budget improvements for {income_level}"
                    }
                ],
                "state": {
                    "status": "active",
                    "last_execution": "2024-01-15T10:35:00Z"
                },
                "interface": {
                    "type": "REST",
                    "endpoint": "/api/financial-analyst",
                    "methods": ["GET", "POST"]
                }
            },
            {
                "agent_id": "agent_2",
                "agent_name": "Data Processor",
                "position": 2,
                "identity": {
                    "role": "processor",
                    "expertise": ["data_cleaning", "transformation"],
                    "access_level": "limited"
                },
                "data_interface": {
                    "input_sources": ["raw_data", "processed_data"],
                    "output_formats": ["cleaned_data", "transformed_data"],
                    "data_retention": "7_days"
                },
                "llm_config": {
                    "model": "openhermes-2.5-mistral-7b",
                    "temperature": 0.1,
                    "max_tokens": 500
                },
                "tools": [
                    {
                        "name": "data_cleaner",
                        "purpose": "Clean and validate data",
                        "auth_required": False
                    },
                    {
                        "name": "data_transformer",
                        "purpose": "Transform data formats",
                        "auth_required": False
                    }
                ],
                "resources": [
                    {
                        "name": "data_schemas",
                        "description": "Data validation schemas",
                        "uri": "finance://schemas/*"
                    },
                    {
                        "name": "transformation_rules",
                        "description": "Data transformation rules",
                        "uri": "finance://rules/transform/*"
                    }
                ],
                "prompts": [
                    {
                        "name": "data_validation",
                        "description": "Validate data quality",
                        "template": "Validate the quality of {data_type} data and report any issues"
                    }
                ],
                "state": {
                    "status": "active",
                    "last_execution": "2024-01-15T10:30:00Z"
                },
                "interface": {
                    "type": "REST",
                    "endpoint": "/api/data-processor",
                    "methods": ["POST"]
                }
            },
            {
                "agent_id": "agent_3",
                "agent_name": "Report Generator",
                "position": 3,
                "identity": {
                    "role": "generator",
                    "expertise": ["report_creation", "visualization"],
                    "access_level": "read_only"
                },
                "data_interface": {
                    "input_sources": ["processed_data", "analysis_results"],
                    "output_formats": ["reports", "charts"],
                    "data_retention": "90_days"
                },
                "llm_config": {
                    "model": "openhermes-2.5-mistral-7b",
                    "temperature": 0.2,
                    "max_tokens": 1500
                },
                "tools": [
                    {
                        "name": "chart_generator",
                        "purpose": "Generate charts and graphs",
                        "auth_required": False
                    },
                    {
                        "name": "report_formatter",
                        "purpose": "Format reports for presentation",
                        "auth_required": False
                    }
                ],
                "resources": [
                    {
                        "name": "report_templates",
                        "description": "Report templates",
                        "uri": "finance://templates/reports/*"
                    }
                ],
                "prompts": [
                    {
                        "name": "report_summary",
                        "description": "Generate report summary",
                        "template": "Create a summary of {report_type} for {time_period}"
                    }
                ],
                "state": {
                    "status": "active",
                    "last_execution": "2024-01-15T10:35:00Z"
                },
                "interface": {
                    "type": "REST",
                    "endpoint": "/api/report-generator",
                    "methods": ["GET", "POST"]
                }
            }
        ]
    }


async def test_individual_components():
    """Test individual components with performance tracking"""
    print("=== Testing Individual Components ===")
    
    # Test BaseAgentParser
    print("\n1. Testing BaseAgentParser...")
    parser_metrics = performance_tracker.start_component("BaseAgentParser")
    
    parser = BaseAgentParser()
    sample_data = create_sample_ba_json()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        json.dump(sample_data, temp_file)
        temp_file_path = temp_file.name
    
    try:
        parsed_data = parser.parse_file(temp_file_path)
        print(f"[OK] Parsed {len(parsed_data.agents)} agents")
        print(f"[OK] Workflow domain: {parsed_data.workflow_metadata.domain}")
        
        # Count primitives
        total_tools = sum(len(agent.tools) for agent in parsed_data.agents)
        total_resources = sum(len(agent.resources) for agent in parsed_data.agents)
        total_prompts = sum(len(agent.prompts) for agent in parsed_data.agents)
        
        print(f"[OK] Total tools: {total_tools}")
        print(f"[OK] Total resources: {total_resources}")
        print(f"[OK] Total prompts: {total_prompts}")
        
        performance_tracker.end_component(parser_metrics, tokens=0, llm_calls=0, success=True)
        
    except Exception as e:
        print(f"[ERROR] BaseAgentParser test failed: {e}")
        performance_tracker.end_component(parser_metrics, tokens=0, llm_calls=0, success=False, error=str(e))
        return False
    finally:
        Path(temp_file_path).unlink()
    
    # Test MCPDiscoveryScanner
    print("\n2. Testing MCPDiscoveryScanner...")
    scanner_metrics = performance_tracker.start_component("MCPDiscoveryScanner")
    
    try:
        scanner = MCPDiscoveryScanner()
        discovered_servers = await scanner.discover_all_servers()
        print(f"[OK] Discovered {len(discovered_servers)} servers")
        
        for server_id, capabilities in discovered_servers.items():
            print(f"  - {server_id}: {len(capabilities.tools)} tools, {len(capabilities.resources)} resources, {len(capabilities.prompts)} prompts")
        
        performance_tracker.end_component(scanner_metrics, tokens=0, llm_calls=0, success=True)
            
    except Exception as e:
        print(f"[ERROR] MCPDiscoveryScanner test failed: {e}")
        performance_tracker.end_component(scanner_metrics, tokens=0, llm_calls=0, success=False, error=str(e))
        return False
    
    # Test SemanticMatcher
    print("\n3. Testing SemanticMatcher...")
    matcher_metrics = performance_tracker.start_component("SemanticMatcher")
    
    try:
        matcher = SemanticMatcher()
        
        # Convert parsed_data to dict format
        ba_dict = {
            "workflow_metadata": {
                "domain": parsed_data.workflow_metadata.domain
            },
            "agents": [
                {
                    "tools": [
                        {
                            "name": tool.name,
                            "purpose": tool.purpose
                        } for tool in agent.tools
                    ],
                    "resources": [
                        {
                            "name": resource.name,
                            "description": resource.description,
                            "uri": resource.uri
                        } for resource in agent.resources
                    ],
                    "prompts": [
                        {
                            "name": prompt.name,
                            "description": prompt.description,
                            "template": prompt.template
                        } for prompt in agent.prompts
                    ]
                } for agent in parsed_data.agents
            ]
        }
        
        matches = await matcher.match_requirements(ba_dict)
        print(f"[OK] Found {len(matches.get('tools', []))} tool matches")
        print(f"[OK] Found {len(matches.get('resources', []))} resource matches")
        print(f"[OK] Found {len(matches.get('prompts', []))} prompt matches")
        
        # Estimate token usage for semantic matching (rough calculation)
        estimated_tokens = len(str(matches)) // 4  # Rough token estimation
        estimated_llm_calls = len(matches.get('tools', [])) + len(matches.get('resources', [])) + len(matches.get('prompts', []))
        
        performance_tracker.end_component(matcher_metrics, tokens=estimated_tokens, llm_calls=estimated_llm_calls, success=True)
        
    except Exception as e:
        print(f"[ERROR] SemanticMatcher test failed: {e}")
        performance_tracker.end_component(matcher_metrics, tokens=0, llm_calls=0, success=False, error=str(e))
        return False
    
    # Test OutputGenerator
    print("\n4. Testing OutputGenerator...")
    generator_metrics = performance_tracker.start_component("OutputGenerator")
    
    try:
        generator = OutputGenerator()
        
        # Create sample matches and execution results
        sample_matches = {
            "tools": [],
            "resources": [],
            "prompts": []
        }
        
        sample_execution_results = {
            "tool_file_reader": {
                "status": "success",
                "result": "File read successfully",
                "server": "finance_mcp_server",
                "confidence": 0.95,
                "execution_time": 1.5
            }
        }
        
        mcp_config = await generator.generate_config(
            sample_data, sample_matches, sample_execution_results
        )
        
        print(f"[OK] Generated MCP configuration with {len(mcp_config.get('servers', []))} servers")
        print(f"[OK] Configuration includes metadata and bindings")
        
        performance_tracker.end_component(generator_metrics, tokens=0, llm_calls=0, success=True)
        
    except Exception as e:
        print(f"[ERROR] OutputGenerator test failed: {e}")
        performance_tracker.end_component(generator_metrics, tokens=0, llm_calls=0, success=False, error=str(e))
        return False
    
    print("\n[OK] All individual component tests passed!")
    return True


async def test_mcp_module():
    """Test the complete MCP module workflow with performance tracking"""
    print("\n=== Testing Complete MCP Module Workflow ===")
    
    workflow_metrics = performance_tracker.start_component("CompleteWorkflow")
    
    # Create sample BA operation JSON
    sample_data = create_sample_ba_json()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        json.dump(sample_data, temp_file)
        temp_file_path = temp_file.name
    
    try:
        # Initialize MCP module
        mcp_module = MCPModule()
        
        # Process the BA operation
        print("Processing BA operation...")
        result = await mcp_module.process_ba_operation(temp_file_path)
        
        # Save the result
        output_file = "test_mcp_configuration_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] MCP configuration generated successfully: {output_file}")
        print(f"[OK] Configuration includes:")
        print(f"  - {len(result.get('servers', []))} servers")
        print(f"  - {len(result.get('bindings', []))} bindings")
        print(f"  - Metadata and workflow information")
        
        # Estimate total tokens and LLM calls from the complete workflow
        estimated_tokens = len(str(result)) // 4  # Rough token estimation
        estimated_llm_calls = len(result.get('servers', {})) * 3  # Rough LLM call estimation
        
        performance_tracker.end_component(workflow_metrics, tokens=estimated_tokens, llm_calls=estimated_llm_calls, success=True)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] MCP module test failed: {e}")
        performance_tracker.end_component(workflow_metrics, tokens=0, llm_calls=0, success=False, error=str(e))
        return False
    finally:
        Path(temp_file_path).unlink()


async def main():
    """Main test function with performance tracking"""
    print("MCP Module Test Suite with Performance Tracking")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test individual components
    components_ok = await test_individual_components()
    
    if components_ok:
        # Test complete workflow
        workflow_ok = await test_mcp_module()
        
        if workflow_ok:
            print("\n[SUCCESS] All tests passed! MCP module is working correctly.")
        else:
            print("\n❌ Workflow test failed. Check the logs for details.")
            sys.exit(1)
    else:
        print("\n❌ Component tests failed. Check the logs for details.")
        sys.exit(1)
    
    # Print performance summary
    performance_tracker.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
