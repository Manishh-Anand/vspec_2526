"""
Base Agent Parser Implementation
"""

import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ToolRequirement:
    """Tool requirement from BA_op.json"""
    name: str
    server: str
    purpose: str
    auth_required: bool


@dataclass
class ResourceRequirement:
    """Resource requirement from BA_op.json"""
    name: str
    description: str
    domain: str
    uri: str
    mime_type: Optional[str] = None


@dataclass
class PromptRequirement:
    """Prompt requirement from BA_op.json"""
    name: str
    description: str
    domain: str
    template: str
    arguments: List[Dict[str, Any]]


@dataclass
class AgentIdentity:
    """Agent identity information"""
    role: str
    agent_type: str
    description: str


@dataclass
class DataInterface:
    """Agent data interface"""
    input: Dict[str, Any]
    output: Dict[str, Any]


@dataclass
class LLMConfig:
    """LLM configuration"""
    provider: str
    model: str
    params: Dict[str, Any]
    reasoning: str


@dataclass
class AgentInterface:
    """Agent interface configuration"""
    primary_method: str
    dependencies: List[str]
    outputs_to: List[str]
    error_strategy: str


@dataclass
class Agent:
    """Agent definition from BA_op.json"""
    agent_id: str
    agent_name: str
    position: int
    identity: AgentIdentity
    data_interface: DataInterface
    llm_config: LLMConfig
    tools: List[ToolRequirement]
    resources: List[ResourceRequirement]  # Added resources
    prompts: List[PromptRequirement]      # Added prompts
    state: Dict[str, Any]
    interface: AgentInterface


@dataclass
class WorkflowMetadata:
    """Workflow metadata"""
    workflow_id: str
    domain: str
    selected_architecture: str
    complexity_level: str
    total_agents: int
    estimated_execution_time: str


@dataclass
class Orchestration:
    """Orchestration configuration"""
    pattern: str
    connections: List[Dict[str, Any]]


@dataclass
class DomainConfig:
    """Domain configuration"""
    security: str
    compliance: List[str]
    constraints: Dict[str, Any]


@dataclass
class BaseAgentOutput:
    """Complete BA_op.json structure"""
    workflow_metadata: WorkflowMetadata
    agents: List[Agent]
    orchestration: Orchestration
    domain_config: DomainConfig


class BaseAgentParser:
    """Parser for BA_op.json files"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_file(self, file_path: str) -> BaseAgentOutput:
        """Parse a BA_op.json file"""
        try:
            self.logger.info(f"Parsing BA_op.json file: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return self.parse_data(data)
            
        except Exception as e:
            self.logger.error(f"Error parsing file {file_path}: {e}")
            raise
    
    def parse_data(self, data: Dict[str, Any]) -> BaseAgentOutput:
        """Parse BA_op.json data"""
        try:
            # Validate structure
            self._validate_structure(data)
            
            # Parse workflow metadata
            workflow_metadata = self._parse_workflow_metadata(data.get("workflow_metadata", {}))
            
            # Parse agents
            agents = []
            for agent_data in data.get("agents", []):
                agent = self._parse_agent(agent_data)
                agents.append(agent)
            
            # Parse orchestration
            orchestration = self._parse_orchestration(data.get("orchestration", {}))
            
            # Parse domain config
            domain_config = self._parse_domain_config(data.get("domain_config", {}))
            
            self.logger.info(f"Successfully parsed {len(agents)} agents for domain: {workflow_metadata.domain}")
            
            return BaseAgentOutput(
                workflow_metadata=workflow_metadata,
                agents=agents,
                orchestration=orchestration,
                domain_config=domain_config
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing BA_op.json data: {e}")
            raise
    
    def _validate_structure(self, data: Dict[str, Any]):
        """Validate the structure of BA_op.json"""
        required_fields = ["workflow_metadata", "agents"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(data.get("agents"), list):
            raise ValueError("Agents must be a list")
    
    def _parse_workflow_metadata(self, metadata_data: Dict[str, Any]) -> WorkflowMetadata:
        """Parse workflow metadata"""
        return WorkflowMetadata(
            workflow_id=metadata_data.get("workflow_id", ""),
            domain=metadata_data.get("domain", ""),
            selected_architecture=metadata_data.get("selected_architecture", ""),
            complexity_level=metadata_data.get("complexity_level", ""),
            total_agents=metadata_data.get("total_agents", 0),
            estimated_execution_time=metadata_data.get("estimated_execution_time", "")
        )
    
    def _parse_agent(self, agent_data: Dict[str, Any]) -> Agent:
        """Parse agent data"""
        try:
            # Parse identity
            identity_data = agent_data.get('identity', {})
            identity = AgentIdentity(
                role=identity_data.get('role', ''),
                agent_type=identity_data.get('agent_type', ''),
                description=identity_data.get('description', '')
            )
            
            # Parse data interface
            data_interface_data = agent_data.get('data_interface', {})
            data_interface = DataInterface(
                input=data_interface_data.get('input', {}),
                output=data_interface_data.get('output', {})
            )
            
            # Parse LLM config
            llm_config_data = agent_data.get('llm_config', {})
            llm_config = LLMConfig(
                provider=llm_config_data.get('provider', ''),
                model=llm_config_data.get('model', ''),
                params=llm_config_data.get('params', {}),
                reasoning=llm_config_data.get('reasoning', '')
            )
            
            # Parse tools
            tools = []
            for tool_data in agent_data.get('tools', []):
                tool = ToolRequirement(
                    name=tool_data.get('name', ''),
                    server=tool_data.get('server', ''),
                    purpose=tool_data.get('purpose', ''),
                    auth_required=tool_data.get('auth_required', False)
                )
                tools.append(tool)
            
            # Parse resources (NEW)
            resources = []
            for resource_data in agent_data.get('resources', []):
                resource = ResourceRequirement(
                    name=resource_data.get('name', ''),
                    description=resource_data.get('description', ''),
                    domain=resource_data.get('domain', ''),
                    uri=resource_data.get('uri', ''),
                    mime_type=resource_data.get('mime_type')
                )
                resources.append(resource)
            
            # Parse prompts (NEW)
            prompts = []
            for prompt_data in agent_data.get('prompts', []):
                prompt = PromptRequirement(
                    name=prompt_data.get('name', ''),
                    description=prompt_data.get('description', ''),
                    domain=prompt_data.get('domain', ''),
                    template=prompt_data.get('template', ''),
                    arguments=prompt_data.get('arguments', [])
                )
                prompts.append(prompt)
            
            # Parse interface
            interface_data = agent_data.get('interface', {})
            interface = AgentInterface(
                primary_method=interface_data.get('primary_method', ''),
                dependencies=interface_data.get('dependencies', []),
                outputs_to=interface_data.get('outputs_to', []),
                error_strategy=interface_data.get('error_strategy', '')
            )
            
            return Agent(
                agent_id=agent_data.get('agent_id', ''),
                agent_name=agent_data.get('agent_name', ''),
                position=agent_data.get('position', 0),
                identity=identity,
                data_interface=data_interface,
                llm_config=llm_config,
                tools=tools,
                resources=resources,  # Added resources
                prompts=prompts,      # Added prompts
                state=agent_data.get('state', {}),
                interface=interface
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse agent data: {e}")
            raise
    
    def _parse_orchestration(self, orchestration_data: Dict[str, Any]) -> Orchestration:
        """Parse orchestration configuration"""
        return Orchestration(
            pattern=orchestration_data.get('pattern', ''),
            connections=orchestration_data.get('connections', [])
        )
    
    def _parse_domain_config(self, domain_config_data: Dict[str, Any]) -> DomainConfig:
        """Parse domain configuration"""
        return DomainConfig(
            security=domain_config_data.get('security', ''),
            compliance=domain_config_data.get('compliance', []),
            constraints=domain_config_data.get('constraints', {})
        )
    
    def extract_domain_requirements(self, ba_data: BaseAgentOutput) -> Dict[str, Any]:
        """Extract domain-specific requirements"""
        domain = ba_data.workflow_metadata.domain
        
        # Extract all tools from all agents
        all_tools = []
        all_resources = []  # Added resources
        all_prompts = []    # Added prompts
        
        for agent in ba_data.agents:
            # Add tools
            for tool in agent.tools:
                all_tools.append({
                    'name': tool.name,
                    'purpose': tool.purpose,
                    'server': tool.server,
                    'auth_required': tool.auth_required
                })
            
            # Add resources (NEW)
            for resource in agent.resources:
                all_resources.append({
                    'name': resource.name,
                    'description': resource.description,
                    'uri': resource.uri,
                    'mime_type': resource.mime_type
                })
            
            # Add prompts (NEW)
            for prompt in agent.prompts:
                all_prompts.append({
                    'name': prompt.name,
                    'description': prompt.description,
                    'template': prompt.template,
                    'arguments': prompt.arguments
                })
        
        return {
            'domain': domain,
            'tools': all_tools,
            'resources': all_resources,  # Added resources
            'prompts': all_prompts       # Added prompts
        }
