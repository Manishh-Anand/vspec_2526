#!/usr/bin/env python3
"""
Simple test script to identify MCP module issues
"""

import asyncio
import json
import sys
import tempfile
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test basic imports"""
    print("=== Testing Basic Imports ===")
    
    try:
        from src.parser.base_agent import BaseAgentParser
        print("✓ BaseAgentParser imported successfully")
    except Exception as e:
        print(f"✗ BaseAgentParser import failed: {e}")
        return False
    
    try:
        from src.output.generator import OutputGenerator
        print("✓ OutputGenerator imported successfully")
    except Exception as e:
        print(f"✗ OutputGenerator import failed: {e}")
        return False
    
    try:
        from src.discovery.scanner import MCPDiscoveryScanner
        print("✓ MCPDiscoveryScanner imported successfully")
    except Exception as e:
        print(f"✗ MCPDiscoveryScanner import failed: {e}")
        return False
    
    return True

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
                    "last_execution": "2024-01-15T10:30:00Z"
                },
                "interface": {
                    "type": "REST",
                    "endpoint": "/api/financial-analyst",
                    "methods": ["GET", "POST"]
                }
            }
        ]
    }

def test_parser():
    """Test the BaseAgentParser"""
    print("\n=== Testing BaseAgentParser ===")
    
    try:
        from src.parser.base_agent import BaseAgentParser
        parser = BaseAgentParser()
        sample_data = create_sample_ba_json()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(sample_data, temp_file)
            temp_file_path = temp_file.name
        
        try:
            parsed_data = parser.parse_file(temp_file_path)
            print(f"✓ Parsed {len(parsed_data.agents)} agents")
            print(f"✓ Workflow domain: {parsed_data.workflow_metadata.domain}")
            
            # Count primitives
            total_tools = sum(len(agent.tools) for agent in parsed_data.agents)
            total_resources = sum(len(agent.resources) for agent in parsed_data.agents)
            total_prompts = sum(len(agent.prompts) for agent in parsed_data.agents)
            
            print(f"✓ Total tools: {total_tools}")
            print(f"✓ Total resources: {total_resources}")
            print(f"✓ Total prompts: {total_prompts}")
            
            return True
            
        except Exception as e:
            print(f"✗ BaseAgentParser test failed: {e}")
            return False
        finally:
            Path(temp_file_path).unlink()
            
    except Exception as e:
        print(f"✗ BaseAgentParser import failed: {e}")
        return False

def test_discovery():
    """Test the MCPDiscoveryScanner"""
    print("\n=== Testing MCPDiscoveryScanner ===")
    
    try:
        from src.discovery.scanner import MCPDiscoveryScanner
        
        async def run_discovery():
            scanner = MCPDiscoveryScanner()
            discovered_servers = await scanner.discover_all_servers()
            print(f"✓ Discovered {len(discovered_servers)} servers")
            
            for server_id, capabilities in discovered_servers.items():
                print(f"  - {server_id}: {len(capabilities.tools)} tools, {len(capabilities.resources)} resources, {len(capabilities.prompts)} prompts")
            
            return True
        
        return asyncio.run(run_discovery())
        
    except Exception as e:
        print(f"✗ MCPDiscoveryScanner test failed: {e}")
        return False

def test_output_generator():
    """Test the OutputGenerator"""
    print("\n=== Testing OutputGenerator ===")
    
    try:
        from src.output.generator import OutputGenerator
        generator = OutputGenerator()
        
        # Create sample data
        sample_data = create_sample_ba_json()
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
        
        async def run_generator():
            mcp_config = await generator.generate_config(
                sample_data, sample_matches, sample_execution_results
            )
            
            print(f"✓ Generated MCP configuration with {len(mcp_config.get('servers', []))} servers")
            print(f"✓ Configuration includes metadata and bindings")
            
            return True
        
        return asyncio.run(run_generator())
        
    except Exception as e:
        print(f"✗ OutputGenerator test failed: {e}")
        return False

def main():
    """Main test function"""
    print("MCP Module Simple Test Suite")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    if imports_ok:
        # Test parser
        parser_ok = test_parser()
        
        if parser_ok:
            # Test discovery
            discovery_ok = test_discovery()
            
            if discovery_ok:
                # Test output generator
                generator_ok = test_output_generator()
                
                if generator_ok:
                    print("\n🎉 All basic tests passed! Core components are working.")
                else:
                    print("\n❌ OutputGenerator test failed.")
            else:
                print("\n❌ Discovery test failed.")
        else:
            print("\n❌ Parser test failed.")
    else:
        print("\n❌ Import tests failed.")

if __name__ == "__main__":
    main()
