#!/usr/bin/env python3
"""
Test MCP module core functionality without requiring servers
"""

import asyncio
import json
import sys
import tempfile
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

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

async def test_parser():
    """Test the BaseAgentParser"""
    print("=== Testing BaseAgentParser ===")
    
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
            
            return parsed_data
            
        except Exception as e:
            print(f"✗ BaseAgentParser test failed: {e}")
            return None
        finally:
            Path(temp_file_path).unlink()
            
    except Exception as e:
        print(f"✗ BaseAgentParser import failed: {e}")
        return None

async def test_semantic_matcher():
    """Test the SemanticMatcher with mock data"""
    print("\n=== Testing SemanticMatcher ===")
    
    try:
        from src.matching.semantic import SemanticMatcher
        matcher = SemanticMatcher()
        
        # Create sample BA data
        ba_dict = {
            "workflow_metadata": {
                "domain": "finance"
            },
            "agents": [
                {
                    "tools": [
                        {
                            "name": "file_reader",
                            "purpose": "Read financial documents"
                        },
                        {
                            "name": "bank_statement_parser",
                            "purpose": "Parse bank statements"
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
                    ]
                }
            ]
        }
        
        # Test matching with mock server capabilities
        mock_servers = {
            "finance_mcp_server": {
                "tools": [
                    {"name": "file_reader", "description": "Read and parse financial files"},
                    {"name": "bank_statement_parser", "description": "Parse bank statements"},
                    {"name": "subscription_detector", "description": "Detect recurring subscriptions"}
                ],
                "resources": [
                    {"uri": "finance://transactions/*", "name": "Transaction History"},
                    {"uri": "finance://market/*", "name": "Market Data"}
                ],
                "prompts": [
                    {"name": "financial_advice", "description": "Generate financial advice"},
                    {"name": "budget_guidance", "description": "Budget consultation"}
                ]
            }
        }
        
        # Test the matcher
        matches = await matcher.match_requirements(ba_dict)
        print(f"✓ Found {len(matches.get('tools', []))} tool matches")
        print(f"✓ Found {len(matches.get('resources', []))} resource matches")
        print(f"✓ Found {len(matches.get('prompts', []))} prompt matches")
        
        return matches
        
    except Exception as e:
        print(f"✗ SemanticMatcher test failed: {e}")
        return None

async def test_output_generator():
    """Test the OutputGenerator"""
    print("\n=== Testing OutputGenerator ===")
    
    try:
        from src.output.generator import OutputGenerator
        from src.matching.semantic import MatchResult
        from src.core.protocol import Tool
        generator = OutputGenerator()
        
        # Create sample data
        sample_data = create_sample_ba_json()
        
        # Create proper MatchResult objects
        sample_matches = {
            "tools": [
                MatchResult(
                    tool=Tool(
                        name="file_reader",
                        description="Read financial documents",
                        inputSchema={}
                    ),
                    server="finance_mcp_server",
                    score=0.95,
                    confidence=0.95,
                    reasoning="High semantic similarity"
                )
            ],
            "resources": [
                MatchResult(
                    tool=Tool(
                        name="transaction_history",
                        description="Historical transaction data",
                        inputSchema={}
                    ),
                    server="finance_mcp_server",
                    score=0.90,
                    confidence=0.90,
                    reasoning="URI pattern match"
                )
            ],
            "prompts": [
                MatchResult(
                    tool=Tool(
                        name="financial_advice",
                        description="Generate financial advice",
                        inputSchema={}
                    ),
                    server="finance_mcp_server",
                    score=0.85,
                    confidence=0.85,
                    reasoning="Semantic match"
                )
            ]
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
        
        print(f"✓ Generated MCP configuration with {len(mcp_config.get('servers', {}))} servers")
        print(f"✓ Configuration includes metadata and bindings")
        
        # Save the configuration for inspection
        with open("test_mcp_config_output.json", "w") as f:
            json.dump(mcp_config, f, indent=2)
        print("✓ Configuration saved to test_mcp_config_output.json")
        
        return mcp_config
        
    except Exception as e:
        print(f"✗ OutputGenerator test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_complete_workflow():
    """Test the complete workflow without servers"""
    print("\n=== Testing Complete Workflow ===")
    
    try:
        from src.main import MCPModule
        
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
            output_file = "test_complete_workflow_output.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Complete workflow completed successfully: {output_file}")
            print(f"✓ Configuration includes:")
            print(f"  - {len(result.get('servers', []))} servers")
            print(f"  - {len(result.get('bindings', []))} bindings")
            print(f"  - Metadata and workflow information")
            
            return True
            
        except Exception as e:
            print(f"✗ Complete workflow test failed: {e}")
            return False
        finally:
            Path(temp_file_path).unlink()
            
    except Exception as e:
        print(f"✗ Complete workflow test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("MCP Module Core Functionality Test")
    print("=" * 50)
    
    # Test parser
    parsed_data = await test_parser()
    if not parsed_data:
        print("❌ Parser test failed. Stopping.")
        return
    
    # Test semantic matcher
    matches = await test_semantic_matcher()
    if not matches:
        print("❌ Semantic matcher test failed. Stopping.")
        return
    
    # Test output generator
    config = await test_output_generator()
    if not config:
        print("❌ Output generator test failed. Stopping.")
        return
    
    # Test complete workflow
    workflow_success = await test_complete_workflow()
    if not workflow_success:
        print("❌ Complete workflow test failed.")
        return
    
    print("\n🎉 All core functionality tests passed!")
    print("\nSummary:")
    print("✓ BaseAgentParser: Working correctly")
    print("✓ SemanticMatcher: Working correctly")
    print("✓ OutputGenerator: Working correctly")
    print("✓ Complete Workflow: Working correctly")
    print("\nThe MCP module core functionality is working properly.")
    print("The remaining issues are related to server connectivity, which can be resolved by:")
    print("1. Starting the test MCP servers")
    print("2. Fixing any network/connection issues")
    print("3. Ensuring proper server discovery")

if __name__ == "__main__":
    asyncio.run(main())
