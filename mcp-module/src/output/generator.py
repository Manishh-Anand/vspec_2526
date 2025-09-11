"""
Output Generator Implementation
"""

import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from src.core.protocol import Tool
from datetime import datetime
from pathlib import Path

from ..matching.semantic import MatchResult
# ExecutionResult is no longer used, execution results are now Dict[str, Any]


class OutputGenerator:
    """Generator for MCP configuration output"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def generate_config(self, ba_data: Dict[str, Any], matches: Dict[str, List[MatchResult]], 
                            execution_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Generate final MCP configuration"""
        try:
            self.logger.info("Generating MCP configuration output")
            
            # Convert dataclass to dict if needed
            if hasattr(ba_data, 'workflow_metadata'):
                # It's a dataclass, convert to dict
                ba_dict = {
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
                                    "server": tool.server,
                                    "purpose": tool.purpose,
                                    "auth_required": tool.auth_required
                                } for tool in agent.tools
                            ],
                            "state": agent.state,
                            "interface": {
                                "primary_method": agent.interface.primary_method,
                                "dependencies": agent.interface.dependencies,
                                "outputs_to": agent.interface.outputs_to,
                                "error_strategy": agent.interface.error_strategy
                            }
                        } for agent in ba_data.agents
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
                # It's already a dict
                ba_dict = ba_data
            
            # Create the main configuration structure
            mcp_config = {
                "metadata": self._generate_metadata(ba_dict),
                "servers": self._generate_servers_config(matches, execution_results),
                "bindings": self._generate_bindings(matches, execution_results),
                "workflow": self._generate_workflow_config(ba_dict, matches),
                "execution_summary": self._generate_execution_summary(execution_results),
                "capabilities": self._generate_capabilities_summary(matches),
                "generated_at": datetime.now().isoformat()
            }
            
            self.logger.info("MCP configuration generated successfully")
            return mcp_config
            
        except Exception as e:
            self.logger.error(f"Error generating MCP configuration: {e}")
            raise
    
    def _generate_metadata(self, ba_data: Any) -> Dict[str, Any]:
        """Generate metadata section"""
        # Handle both objects and dictionaries
        if hasattr(ba_data, 'workflow_metadata'):
            workflow_metadata = ba_data.workflow_metadata
            return {
                "workflow_id": workflow_metadata.workflow_id,
                "workflow_name": "Unknown Workflow",
                "domain": workflow_metadata.domain,
                "version": "1.0.0",
                "description": "",
                "created_by": "mcp-module",
                "created_at": datetime.now().isoformat(),
                "mcp_module_version": "1.0.0",
                "protocol_version": "2024-11-05"
            }
        elif isinstance(ba_data, dict):
            workflow_metadata = ba_data.get("workflow_metadata", {})
            return {
                "workflow_id": workflow_metadata.get("workflow_id", "unknown"),
                "workflow_name": workflow_metadata.get("workflow_name", "Unknown Workflow"),
                "domain": workflow_metadata.get("domain", "unknown"),
                "version": workflow_metadata.get("version", "1.0.0"),
                "description": workflow_metadata.get("description", ""),
                "created_by": workflow_metadata.get("created_by", "mcp-module"),
                "created_at": workflow_metadata.get("created_at", datetime.now().isoformat()),
                "mcp_module_version": "1.0.0",
                "protocol_version": "2024-11-05"
            }
        else:
            return {
                "workflow_id": "unknown",
                "workflow_name": "Unknown Workflow",
                "domain": "unknown",
                "version": "1.0.0",
                "description": "",
                "created_by": "mcp-module",
                "created_at": datetime.now().isoformat(),
                "mcp_module_version": "1.0.0",
                "protocol_version": "2024-11-05"
            }
    
    def _generate_servers_config(self, matches: Dict[str, List[MatchResult]], 
                               execution_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Generate servers configuration"""
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Generating servers config. Matches type: {type(matches)}, Execution results type: {type(execution_results)}")
        if isinstance(matches, dict):
            logger.info(f"Matches keys: {list(matches.keys())}")
            for key, value in matches.items():
                logger.info(f"  {key}: {type(value)}, length: {len(value) if hasattr(value, '__len__') else 'N/A'}")
        else:
            logger.info(f"Matches is not a dict: {matches}")
        
        servers_config = {}
        
        # Group matches by server
        server_matches = {}
        for category, match_list in matches.items():
            for match in match_list:
                # Handle both MatchResult objects and dictionaries
                if hasattr(match, 'server'):
                    server = match.server
                elif isinstance(match, dict):
                    server = match.get('server', 'unknown_server')
                else:
                    server = 'unknown_server'
                    
                if server not in server_matches:
                    server_matches[server] = {"tools": [], "resources": [], "prompts": []}
                server_matches[server][category].append(match)
        
        # Generate configuration for each server with matches
        for server_name, server_data in server_matches.items():
            server_config = {
                "transport": {
                    "type": "stdio",
                    "command": self._get_server_command(server_name)
                },
                "capabilities": {
                    "tools": self._format_tools_config(server_data.get("tools", [])),
                    "resources": self._format_resources_config(server_data.get("resources", [])),
                    "prompts": self._format_prompts_config(server_data.get("prompts", []))
                },
                "execution_stats": self._get_server_execution_stats(server_name, execution_results),
                "status": "active"
            }
            
            servers_config[server_name] = server_config
        
        # Also add discovered servers that don't have matches
        # This ensures all discovered servers are included in the output
        discovered_servers = self._get_discovered_servers_from_matches(matches)
        for server_name in discovered_servers:
            if server_name not in servers_config:
                server_config = {
                    "transport": {
                        "type": "http",  # Default to HTTP for discovered servers
                        "endpoint": f"http://localhost:3001/mcp" if "3001" in server_name else f"http://localhost:3002/mcp"
                    },
                    "capabilities": {
                        "tools": [],
                        "resources": [],
                        "prompts": []
                    },
                    "execution_stats": self._get_server_execution_stats(server_name, execution_results),
                    "status": "discovered"
                }
                
                servers_config[server_name] = server_config
        
        return servers_config
    
    def _get_discovered_servers_from_matches(self, matches: Dict[str, List[MatchResult]]) -> List[str]:
        """Extract discovered server names from matches"""
        discovered_servers = set()
        
        # Extract server names from matches
        for category, match_list in matches.items():
            for match in match_list:
                if hasattr(match, 'server'):
                    discovered_servers.add(match.server)
                elif isinstance(match, dict):
                    server = match.get('server', '')
                    if server:
                        discovered_servers.add(server)
                else:
                    continue
        
        # Add default discovered servers if no matches found
        if not discovered_servers:
            discovered_servers = {
                "network_127.0.0.1_3001",
                "network_localhost_3001"
            }
        
        return list(discovered_servers)
    
    def _get_server_command(self, server_name: str) -> List[str]:
        """Get the command to start a server"""
        server_scripts = {
            "finance_mcp_server": "servers/finance/server.py",
            "productivity_mcp_server": "servers/productivity/server.py",
            "education_mcp_server": "servers/education/server.py",
            "sports_mcp_server": "servers/sports/server.py",
            "software_dev_mcp_server": "servers/software_dev/server.py"
        }
        
        script_path = server_scripts.get(server_name, "")
        if script_path:
            return ["python", script_path]
        else:
            return ["python", "unknown_server.py"]
    
    def _format_tools_config(self, tool_matches: List[MatchResult]) -> List[Dict[str, Any]]:
        """Format tools configuration"""
        tools_config = []
        
        for match in tool_matches:
            # Handle both MatchResult objects and dictionaries
            if hasattr(match, 'tool'):
                tool_name = match.tool.name
                tool_description = match.tool.description
                match_score = match.score
                confidence = match.confidence
                reasoning = match.reasoning
                parameters = match.tool.parameters if hasattr(match.tool, 'parameters') else {}
            elif isinstance(match, dict):
                tool_name = match.get('tool_name', match.get('name', 'unknown_tool'))
                tool_description = match.get('description', '')
                match_score = match.get('score', 0.0)
                confidence = match.get('confidence', 0.0)
                reasoning = match.get('reasoning', '')
                parameters = match.get('parameters', {})
            else:
                continue
                
            tool_config = {
                "name": tool_name,
                "description": tool_description,
                "match_score": match_score,
                "confidence": confidence,
                "reasoning": reasoning,
                "parameters": parameters,
                "auth_required": False
            }
            tools_config.append(tool_config)
        
        return tools_config
    
    def _format_resources_config(self, resource_matches: List[MatchResult]) -> List[Dict[str, Any]]:
        """Format resources configuration"""
        resources_config = []
        
        for match in resource_matches:
            # Handle both MatchResult objects and dictionaries
            if hasattr(match, 'tool'):
                resource_uri = match.tool.name
                resource_name = match.tool.description
                match_score = match.score
                confidence = match.confidence
                reasoning = match.reasoning
            elif isinstance(match, dict):
                resource_uri = match.get('resource_name', match.get('name', 'unknown_resource'))
                resource_name = match.get('description', '')
                match_score = match.get('score', 0.0)
                confidence = match.get('confidence', 0.0)
                reasoning = match.get('reasoning', '')
            else:
                continue
                
            resource_config = {
                "uri": resource_uri,
                "name": resource_name,
                "match_score": match_score,
                "confidence": confidence,
                "reasoning": reasoning,
                "mime_type": "application/json"
            }
            resources_config.append(resource_config)
        
        return resources_config
    
    def _format_prompts_config(self, prompt_matches: List[MatchResult]) -> List[Dict[str, Any]]:
        """Format prompts configuration"""
        prompts_config = []
        
        for match in prompt_matches:
            # Handle both MatchResult objects and dictionaries
            if hasattr(match, 'tool'):
                prompt_name = match.tool.name
                arguments = match.tool.parameters if hasattr(match.tool, 'parameters') else {}
                match_score = match.score
                confidence = match.confidence
                reasoning = match.reasoning
            elif isinstance(match, dict):
                prompt_name = match.get('prompt_name', match.get('name', 'unknown_prompt'))
                arguments = match.get('arguments', {})
                match_score = match.get('score', 0.0)
                confidence = match.get('confidence', 0.0)
                reasoning = match.get('reasoning', '')
            else:
                continue
                
            prompt_config = {
                "name": prompt_name,
                "arguments": arguments,
                "match_score": match_score,
                "confidence": confidence,
                "reasoning": reasoning
            }
            prompts_config.append(prompt_config)
        
        return prompts_config
    
    def _get_server_execution_stats(self, server_name: str, execution_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Get execution statistics for a server"""
        stats = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "average_execution_time": 0.0,
            "total_execution_time": 0.0
        }
        
        total_time = 0.0
        successful_count = 0
        
        for category, results in execution_results.items():
            for result in results:
                # Handle execution results as dictionaries
                if isinstance(result, dict):
                    result_server = result.get('server', 'unknown_server')
                    result_success = result.get('success', False)
                    result_execution_time = result.get('execution_time', 0.0)
                else:
                    continue
                    
                if result_server == server_name:
                    stats["total_operations"] += 1
                    total_time += result_execution_time
                    
                    if result_success:
                        stats["successful_operations"] += 1
                        successful_count += 1
                    else:
                        stats["failed_operations"] += 1
        
        if stats["total_operations"] > 0:
            stats["average_execution_time"] = total_time / stats["total_operations"]
            stats["total_execution_time"] = total_time
        
        return stats
    
    def _generate_workflow_config(self, ba_data: Dict[str, Any], matches: Dict[str, List[MatchResult]]) -> Dict[str, Any]:
        """Generate workflow configuration"""
        workflow_config = {
            "agents": self._format_agents_config(ba_data.get("agents", []), matches),
            "orchestration": self._format_orchestration_config(ba_data.get("orchestration", {})),
            "domain_config": self._format_domain_config(ba_data.get("domain_config", {}))
        }
        
        return workflow_config
    
    def _format_agents_config(self, agents: List[Dict[str, Any]], matches: Dict[str, List[MatchResult]]) -> List[Dict[str, Any]]:
        """Format agents configuration"""
        formatted_agents = []
        
        for agent in agents:
            # Handle both objects and dictionaries
            if hasattr(agent, 'agent_id'):
                agent_id = agent.agent_id
            elif isinstance(agent, dict):
                agent_id = agent.get("agent_id", "")
            else:
                continue
            
            # Find matched tools for this agent
            agent_tools = []
            for category, match_list in matches.items():
                for match in match_list:
                    # This is a simplified matching - in a real implementation,
                    # you'd have a more sophisticated way to match tools to agents
                    if category == "tools":
                        # Handle both MatchResult objects and dictionaries
                        if hasattr(match, 'tool'):
                            tool_name = match.tool.name
                            server = match.server
                            score = match.score
                            confidence = match.confidence
                        elif isinstance(match, dict):
                            tool_name = match.get('tool_name', match.get('name', 'unknown_tool'))
                            server = match.get('server', 'unknown_server')
                            score = match.get('score', 0.0)
                            confidence = match.get('confidence', 0.0)
                        else:
                            continue
                            
                        agent_tools.append({
                            "name": tool_name,
                            "server": server,
                            "score": score,
                            "confidence": confidence
                        })
            
            # Handle both objects and dictionaries for agent fields
            if hasattr(agent, 'agent_name'):
                agent_name = agent.agent_name
                position = agent.position
                identity = {
                    "role": agent.identity.role,
                    "agent_type": agent.identity.agent_type,
                    "description": agent.identity.description
                }
                data_interface = {
                    "input": agent.data_interface.input,
                    "output": agent.data_interface.output
                }
                llm_config = {
                    "provider": agent.llm_config.provider,
                    "model": agent.llm_config.model,
                    "params": agent.llm_config.params,
                    "reasoning": agent.llm_config.reasoning
                }
                state = agent.state
                interface = {
                    "primary_method": agent.interface.primary_method,
                    "dependencies": agent.interface.dependencies,
                    "outputs_to": agent.interface.outputs_to,
                    "error_strategy": agent.interface.error_strategy
                }
            elif isinstance(agent, dict):
                agent_name = agent.get("agent_name", "")
                position = agent.get("position", 0)
                identity = agent.get("identity", {})
                data_interface = agent.get("data_interface", {})
                llm_config = agent.get("llm_config", {})
                state = agent.get("state", {})
                interface = agent.get("interface", {})
            else:
                continue
                
            formatted_agent = {
                "agent_id": agent_id,
                "agent_name": agent_name,
                "position": position,
                "identity": identity,
                "data_interface": data_interface,
                "llm_config": llm_config,
                "matched_tools": agent_tools,
                "state": state,
                "interface": interface
            }
            
            formatted_agents.append(formatted_agent)
        
        return formatted_agents
    
    def _format_orchestration_config(self, orchestration: Any) -> Dict[str, Any]:
        """Format orchestration configuration"""
        # Handle both objects and dictionaries
        if hasattr(orchestration, 'pattern'):
            return {
                "strategy": "sequential",
                "parallel_execution": False,
                "error_handling": "stop_on_error",
                "retry_policy": {},
                "timeout": 300,
                "dependencies": orchestration.connections if hasattr(orchestration, 'connections') else []
            }
        elif isinstance(orchestration, dict):
            return {
                "strategy": orchestration.get("strategy", "sequential"),
                "parallel_execution": orchestration.get("parallel_execution", False),
                "error_handling": orchestration.get("error_handling", "stop_on_error"),
                "retry_policy": orchestration.get("retry_policy", {}),
                "timeout": orchestration.get("timeout", 300),
                "dependencies": orchestration.get("dependencies", [])
            }
        else:
            return {
                "strategy": "sequential",
                "parallel_execution": False,
                "error_handling": "stop_on_error",
                "retry_policy": {},
                "timeout": 300,
                "dependencies": []
            }
    
    def _format_domain_config(self, domain_config: Any) -> Dict[str, Any]:
        """Format domain configuration"""
        # Handle both objects and dictionaries
        if hasattr(domain_config, 'security'):
            return {
                "domain": "",
                "specific_requirements": [],
                "constraints": {
                    "security": domain_config.security,
                    "compliance": domain_config.compliance if hasattr(domain_config, 'compliance') else [],
                    "constraints": domain_config.constraints if hasattr(domain_config, 'constraints') else {}
                },
                "preferences": {}
            }
        elif isinstance(domain_config, dict):
            return {
                "domain": domain_config.get("domain", ""),
                "specific_requirements": domain_config.get("specific_requirements", []),
                "constraints": domain_config.get("constraints", {}),
                "preferences": domain_config.get("preferences", {})
            }
        else:
            return {
                "domain": "",
                "specific_requirements": [],
                "constraints": {},
                "preferences": {}
            }
    
    def _generate_execution_summary(self, execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate execution summary"""
        summary = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "total_execution_time": 0.0,
            "average_execution_time": 0.0,
            "by_category": {},
            "by_server": {},
            "errors": []
        }
        
        total_time = 0.0
        successful_count = 0
        
        # Handle execution results as dictionaries
        for operation_id, result in execution_results.items():
            summary["total_operations"] += 1
            
            # Extract data from result (dictionary format)
            execution_time = result.get('execution_time', 0.0)
            success = result.get('status') == 'success'
            tool_name = operation_id
            server = result.get('server', 'unknown')
            error = result.get('error', None)
            
            total_time += execution_time
            
            if success:
                summary["successful_operations"] += 1
                successful_count += 1
            else:
                summary["failed_operations"] += 1
                if error:
                    summary["errors"].append({
                        "tool": tool_name,
                        "server": server,
                        "error": error
                    })
        
        # Update server stats (only if we have results)
        if execution_results:
            for operation_id, result in execution_results.items():
                result_server = result.get('server', 'unknown')
                result_execution_time = result.get('execution_time', 0.0)
                result_success = result.get('status') == 'success'
                
                if result_server not in summary["by_server"]:
                    summary["by_server"][result_server] = {
                        "total": 0,
                        "successful": 0,
                        "failed": 0,
                        "total_time": 0.0
                    }
                
                server_stats = summary["by_server"][result_server]
                server_stats["total"] += 1
                server_stats["total_time"] += result_execution_time
                
                if result_success:
                    server_stats["successful"] += 1
                else:
                    server_stats["failed"] += 1
        
        if summary["total_operations"] > 0:
            summary["total_execution_time"] = total_time
            summary["average_execution_time"] = total_time / summary["total_operations"]
        
        # Calculate averages for server stats
        for server_stats in summary["by_server"].values():
            if server_stats["total"] > 0:
                server_stats["average_time"] = server_stats["total_time"] / server_stats["total"]
        
        return summary
    
    def _generate_bindings(self, matches: Dict[str, List[MatchResult]], execution_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate bindings between agents and server capabilities"""
        bindings = []
        
        try:
            # Process tool bindings
            for match in matches.get('tools', []):
                # Handle both MatchResult objects and dictionaries
                if hasattr(match, 'tool'):
                    tool_name = match.tool.name
                    server = match.server
                    confidence = match.confidence
                    score = match.score
                elif isinstance(match, dict):
                    tool_name = match.get('tool_name', match.get('name', 'unknown_tool'))
                    server = match.get('server', 'unknown_server')
                    confidence = match.get('confidence', 0.0)
                    score = match.get('score', 0.0)
                else:
                    continue
                    
                binding = {
                    "binding_id": f"tool_{tool_name}_{server}",
                    "type": "tool",
                    "agent_requirement": tool_name,
                    "server_capability": tool_name,
                    "server": server,
                    "confidence": confidence,
                    "score": score,
                    "status": "matched",
                    "execution_status": execution_results.get(f"tool_{tool_name}", {}).get("status", "pending"),
                    "created_at": datetime.now().isoformat()
                }
                bindings.append(binding)
            
            # Process resource bindings
            for match in matches.get('resources', []):
                # Handle both MatchResult objects and dictionaries
                if hasattr(match, 'tool'):
                    resource_name = match.tool.name
                    server = match.server
                    confidence = match.confidence
                    score = match.score
                elif isinstance(match, dict):
                    resource_name = match.get('resource_name', match.get('name', 'unknown_resource'))
                    server = match.get('server', 'unknown_server')
                    confidence = match.get('confidence', 0.0)
                    score = match.get('score', 0.0)
                else:
                    continue
                    
                binding = {
                    "binding_id": f"resource_{resource_name}_{server}",
                    "type": "resource",
                    "agent_requirement": resource_name,
                    "server_capability": resource_name,
                    "server": server,
                    "confidence": confidence,
                    "score": score,
                    "status": "matched",
                    "execution_status": execution_results.get(f"resource_{resource_name}", {}).get("status", "pending"),
                    "created_at": datetime.now().isoformat()
                }
                bindings.append(binding)
            
            # Process prompt bindings
            for match in matches.get('prompts', []):
                # Handle both MatchResult objects and dictionaries
                if hasattr(match, 'tool'):
                    prompt_name = match.tool.name
                    server = match.server
                    confidence = match.confidence
                    score = match.score
                elif isinstance(match, dict):
                    prompt_name = match.get('prompt_name', match.get('name', 'unknown_prompt'))
                    server = match.get('server', 'unknown_server')
                    confidence = match.get('confidence', 0.0)
                    score = match.get('score', 0.0)
                else:
                    continue
                    
                binding = {
                    "binding_id": f"prompt_{prompt_name}_{server}",
                    "type": "prompt",
                    "agent_requirement": prompt_name,
                    "server_capability": prompt_name,
                    "server": server,
                    "confidence": confidence,
                    "score": score,
                    "status": "matched",
                    "execution_status": execution_results.get(f"prompt_{prompt_name}", {}).get("status", "pending"),
                    "created_at": datetime.now().isoformat()
                }
                bindings.append(binding)
            
            self.logger.info(f"Generated {len(bindings)} bindings")
            return bindings
            
        except Exception as e:
            self.logger.error(f"Error generating bindings: {e}")
            return []
    
    def _generate_capabilities_summary(self, matches: Dict[str, List[MatchResult]]) -> Dict[str, Any]:
        """Generate capabilities summary"""
        summary = {
            "total_matches": 0,
            "by_category": {},
            "by_server": {},
            "match_quality": {
                "high_confidence": 0,
                "medium_confidence": 0,
                "low_confidence": 0
            }
        }
        
        for category, match_list in matches.items():
            category_summary = {
                "count": len(match_list),
                "average_score": 0.0,
                "average_confidence": 0.0
            }
            
            total_score = 0.0
            total_confidence = 0.0
            
            for match in match_list:
                # Handle both MatchResult objects and dictionaries
                if hasattr(match, 'score'):
                    score = match.score
                    confidence = match.confidence
                    server = match.server
                elif isinstance(match, dict):
                    score = match.get('score', 0.0)
                    confidence = match.get('confidence', 0.0)
                    server = match.get('server', 'unknown_server')
                else:
                    continue
                    
                summary["total_matches"] += 1
                total_score += score
                total_confidence += confidence
                
                # Update server stats
                if server not in summary["by_server"]:
                    summary["by_server"][server] = {
                        "count": 0,
                        "average_score": 0.0,
                        "average_confidence": 0.0
                    }
                
                server_stats = summary["by_server"][server]
                server_stats["count"] += 1
                
                # Update confidence levels
                if confidence >= 0.8:
                    summary["match_quality"]["high_confidence"] += 1
                elif confidence >= 0.6:
                    summary["match_quality"]["medium_confidence"] += 1
                else:
                    summary["match_quality"]["low_confidence"] += 1
            
            if category_summary["count"] > 0:
                category_summary["average_score"] = total_score / category_summary["count"]
                category_summary["average_confidence"] = total_confidence / category_summary["count"]
            
            summary["by_category"][category] = category_summary
        
        # Calculate averages for server stats
        for server_stats in summary["by_server"].values():
            if server_stats["count"] > 0:
                # This would need to be calculated properly in a real implementation
                server_stats["average_score"] = 0.8  # Placeholder
                server_stats["average_confidence"] = 0.7  # Placeholder
        
        return summary
    
    async def save_config(self, config: Dict[str, Any], output_path: str) -> str:
        """Save MCP configuration to file"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"MCP configuration saved to {output_path}")
            return str(output_file.absolute())
            
        except Exception as e:
            self.logger.error(f"Error saving MCP configuration: {e}")
            raise
