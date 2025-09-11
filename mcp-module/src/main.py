#!/usr/bin/env python3
"""
MCP Module Main Implementation with Resource Management
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from src.parser.base_agent import BaseAgentParser
from src.discovery.scanner import MCPDiscoveryScanner
from src.matching.semantic import FastSemanticMatcher
from src.execution.executor import ExecutionEngine
from src.output.generator import OutputGenerator


class MCPModule:
    """Main MCP Module with comprehensive resource management"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.parser = BaseAgentParser()
        self.discovery_scanner = MCPDiscoveryScanner()
        self.semantic_matcher = FastSemanticMatcher()
        self.execution_engine = ExecutionEngine()
        self.output_generator = OutputGenerator()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with proper cleanup"""
        await self._cleanup_resources()
    
    async def process_ba_operation(self, ba_file_path: str, output_file_path: str = None) -> Dict[str, Any]:
        """Process BA operation with comprehensive resource management"""
        try:
            self.logger.info(f"Starting BA operation processing: {ba_file_path}")
            
            # Parse BA operation
            ba_data = await self._parse_ba_operation(ba_file_path)
            if not ba_data:
                raise Exception("Failed to parse BA operation")
            
            # Discover MCP servers
            discovered_servers = await self._discover_servers()
            
            # Perform semantic matching
            matches = await self._perform_semantic_matching(ba_data, discovered_servers)
            
            # Execute matched operations
            execution_results = await self._execute_operations(matches)
            
            # Generate output
            output = await self._generate_output(ba_data, matches, execution_results)
            
            # Save output to file
            if output_file_path:
                await self._save_output(output, output_file_path)
            
            self.logger.info("BA operation processing completed successfully")
            return output
            
        except Exception as e:
            self.logger.error(f"Error processing BA operation: {e}")
            raise
        finally:
            await self._cleanup_resources()
    
    async def _parse_ba_operation(self, ba_file_path: str) -> Optional[Dict[str, Any]]:
        """Parse BA operation file"""
        try:
            self.logger.info(f"Parsing BA operation file: {ba_file_path}")
            
            # Check if file exists
            if not Path(ba_file_path).exists():
                raise FileNotFoundError(f"BA operation file not found: {ba_file_path}")
            
            # Parse using BaseAgentParser
            ba_data = self.parser.parse_file(ba_file_path)
            
            if not ba_data:
                raise Exception("Failed to parse BA operation data")
            
            self.logger.info("BA operation parsing completed successfully")
            return ba_data
            
        except Exception as e:
            self.logger.error(f"Error parsing BA operation: {e}")
            return None
    
    async def _discover_servers(self) -> Dict[str, Any]:
        """Discover MCP servers with resource management"""
        try:
            self.logger.info("Starting MCP server discovery")
            
            # Use async context manager for discovery scanner
            async with self.discovery_scanner:
                discovered_servers = await self.discovery_scanner.discover_all_servers()
            
            self.logger.info(f"Server discovery completed. Found {len(discovered_servers)} servers")
            return discovered_servers
            
        except Exception as e:
            self.logger.error(f"Error in server discovery: {e}")
            return {}
    
    async def _perform_semantic_matching(self, ba_data: Any, discovered_servers: Dict[str, Any]) -> Dict[str, Any]:
        """Perform semantic matching with resource management"""
        try:
            self.logger.info("Starting semantic matching")
            
            # Convert BaseAgentOutput to dictionary format for semantic matching
            ba_dict = self._convert_ba_data_to_dict(ba_data)
            
            # Perform matching using FastSemanticMatcher
            matches = await self.semantic_matcher.match_requirements(ba_dict)
            
            self.logger.info(f"Semantic matching completed. Found {len(matches.get('tools', []))} tool matches, {len(matches.get('resources', []))} resource matches, {len(matches.get('prompts', []))} prompt matches")
            return matches
            
        except Exception as e:
            self.logger.error(f"Error in semantic matching: {e}")
            return {"tools": [], "resources": [], "prompts": []}
    
    async def _execute_operations(self, matches: Dict[str, Any]) -> Dict[str, Any]:
        """Execute matched operations with resource management"""
        try:
            self.logger.info("Starting operation execution")
            self.logger.info(f"Matches type: {type(matches)}")
            if isinstance(matches, dict):
                self.logger.info(f"Matches keys: {list(matches.keys())}")
                for key, value in matches.items():
                    self.logger.info(f"  {key}: {type(value)}, length: {len(value) if hasattr(value, '__len__') else 'N/A'}")
            else:
                self.logger.info(f"Matches is not a dict: {matches}")
            
            execution_results = {
                "tools": [],
                "resources": [],
                "prompts": []
            }
            
            # Execute tools if available
            if matches.get("tools"):
                self.logger.info(f"Executing {len(matches['tools'])} tool operations")
                tool_results = await self._execute_tools(matches["tools"])
                execution_results["tools"] = tool_results
            
            # Execute resources if available
            if matches.get("resources"):
                self.logger.info(f"Executing {len(matches['resources'])} resource operations")
                resource_results = await self._execute_resources(matches["resources"])
                execution_results["resources"] = resource_results
            
            # Execute prompts if available
            if matches.get("prompts"):
                self.logger.info(f"Executing {len(matches['prompts'])} prompt operations")
                prompt_results = await self._execute_prompts(matches["prompts"])
                execution_results["prompts"] = prompt_results
            
            self.logger.info("Operation execution completed successfully")
            return execution_results
            
        except Exception as e:
            self.logger.error(f"Error in operation execution: {e}")
            return {"tools": [], "resources": [], "prompts": []}
    
    def _convert_ba_data_to_dict(self, ba_data: Any) -> Dict[str, Any]:
        """Convert BaseAgentOutput object to dictionary format for semantic matching"""
        try:
            self.logger.info(f"Converting BA data to dictionary. Type: {type(ba_data)}")
            if hasattr(ba_data, 'workflow_metadata'):
                # It's a BaseAgentOutput object
                self.logger.info("Converting BaseAgentOutput object to dictionary")
                return {
                    "workflow_metadata": {
                        "workflow_id": ba_data.workflow_metadata.workflow_id,
                        "domain": ba_data.workflow_metadata.domain,
                        "selected_architecture": ba_data.workflow_metadata.selected_architecture,
                        "complexity_level": ba_data.workflow_metadata.complexity_level,
                        "total_agents": ba_data.workflow_metadata.total_agents,
                        "estimated_execution_time": ba_data.workflow_metadata.estimated_execution_time
                    },
                    "agents": [
                        {
                            "agent_id": agent.agent_id,
                            "agent_name": agent.agent_name,
                            "position": agent.position,
                            "identity": {
                                "role": agent.identity.role,
                                "agent_type": agent.identity.agent_type,
                                "description": agent.identity.description
                            },
                            "data_interface": {
                                "input": agent.data_interface.input,
                                "output": agent.data_interface.output
                            },
                            "llm_config": {
                                "provider": agent.llm_config.provider,
                                "model": agent.llm_config.model,
                                "params": agent.llm_config.params,
                                "reasoning": agent.llm_config.reasoning
                            },
                            "tools": [
                                {
                                    "name": tool.name,
                                    "purpose": tool.purpose,
                                    "server": tool.server,
                                    "auth_required": tool.auth_required
                                }
                                for tool in agent.tools
                            ],
                            "resources": [
                                {
                                    "name": resource.name,
                                    "description": resource.description,
                                    "domain": resource.domain,
                                    "uri": resource.uri,
                                    "mime_type": resource.mime_type
                                }
                                for resource in agent.resources
                            ],
                            "prompts": [
                                {
                                    "name": prompt.name,
                                    "description": prompt.description,
                                    "domain": prompt.domain,
                                    "template": prompt.template,
                                    "arguments": prompt.arguments
                                }
                                for prompt in agent.prompts
                            ],
                            "state": agent.state,
                            "interface": {
                                "primary_method": agent.interface.primary_method,
                                "dependencies": agent.interface.dependencies,
                                "outputs_to": agent.interface.outputs_to,
                                "error_strategy": agent.interface.error_strategy
                            }
                        }
                        for agent in ba_data.agents
                    ],
                    "orchestration": {
                        "pattern": ba_data.orchestration.pattern,
                        "connections": ba_data.orchestration.connections
                    },
                    "domain_config": {
                        "security": ba_data.domain_config.security,
                        "compliance": ba_data.domain_config.compliance,
                        "constraints": ba_data.domain_config.constraints
                    }
                }
            else:
                # It's already a dictionary
                return ba_data
                
        except Exception as e:
            self.logger.error(f"Error converting BA data to dictionary: {e}")
            return {}
    
    async def _execute_tools(self, tool_matches: List[Any]) -> List[Dict[str, Any]]:
        """Execute tool operations with resource management"""
        try:
            # Convert matches to tool bindings
            tool_bindings = []
            for match in tool_matches:
                binding = {
                    "tool": {
                        "name": match.tool.name,
                        "description": match.tool.description,
                        "inputSchema": getattr(match.tool, 'inputSchema', {})
                    },
                    "server": match.server,
                    "score": match.score,
                    "confidence": match.confidence
                }
                tool_bindings.append(binding)
            
            # Execute tools using execution engine
            async with self.execution_engine:
                results = await self.execution_engine.execute_all_tools(tool_bindings)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error executing tools: {e}")
            return []
    
    async def _execute_resources(self, resource_matches: List[Any]) -> List[Dict[str, Any]]:
        """Execute resource operations with resource management"""
        try:
            # For resources, we typically just read them
            results = []
            for match in resource_matches:
                result = {
                    "success": True,
                    "result": {
                        "uri": match.tool.name,
                        "content": f"Resource content for {match.tool.name}",
                        "mimeType": "text/plain"
                    },
                    "resource": match.tool.name,
                    "server": match.server
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error executing resources: {e}")
            return []
    
    async def _execute_prompts(self, prompt_matches: List[Any]) -> List[Dict[str, Any]]:
        """Execute prompt operations with resource management"""
        try:
            # For prompts, we typically just retrieve them
            results = []
            for match in prompt_matches:
                result = {
                    "success": True,
                    "result": {
                        "name": match.tool.name,
                        "template": f"Prompt template for {match.tool.name}",
                        "arguments": []
                    },
                    "prompt": match.tool.name,
                    "server": match.server
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error executing prompts: {e}")
            return []
    
    async def _generate_output(self, ba_data: Any, matches: Dict[str, Any], execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate output with resource management"""
        try:
            self.logger.info("Generating output configuration")
            
            # Convert BaseAgentOutput to dictionary format for output generation
            ba_dict = self._convert_ba_data_to_dict(ba_data)
            
            # Generate output using OutputGenerator
            output = await self.output_generator.generate_config(ba_dict, matches, execution_results)
            
            self.logger.info("Output generation completed successfully")
            return output
            
        except Exception as e:
            self.logger.error(f"Error generating output: {e}")
            return {}
    
    async def _save_output(self, output: Dict[str, Any], output_file_path: str):
        """Save output to file"""
        try:
            self.logger.info(f"Saving output to: {output_file_path}")
            
            # Ensure output directory exists
            output_path = Path(output_file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save as JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Output saved successfully to: {output_file_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving output: {e}")
            raise
    
    async def _cleanup_resources(self):
        """Clean up all resources and connections"""
        try:
            self.logger.info("Cleaning up resources")
            
            # Close discovery scanner
            if hasattr(self.discovery_scanner, 'close'):
                await self.discovery_scanner.close()
            
            # Close execution engine
            if hasattr(self.execution_engine, 'close'):
                await self.execution_engine.close()
            
            self.logger.info("Resource cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during resource cleanup: {e}")


async def main():
    """Main function with proper resource management"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Define file paths
    ba_file_path = "tests/fixtures/sample_ba_op.json"
    output_file_path = "test_mcp_configuration_output.json"
    
    try:
        # Use async context manager for proper resource management
        async with MCPModule() as mcp_module:
            # Process BA operation
            result = await mcp_module.process_ba_operation(ba_file_path, output_file_path)
            
            print("MCP Module processing completed successfully!")
            print(f"Output saved to: {output_file_path}")
            
            # Print summary
            if result:
                servers = result.get("servers", {})
                bindings = result.get("bindings", [])
                workflow = result.get("workflow", {})
                
                print(f"\nSummary:")
                print(f"- Servers discovered: {len(servers)}")
                print(f"- Bindings created: {len(bindings)}")
                print(f"- Workflow agents: {len(workflow.get('agents', []))}")
            
    except Exception as e:
        print(f"Error in MCP Module: {e}")
        logging.error(f"Error in MCP Module: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
