"""
MCP Primitives
Tools, Resources, and Prompts definitions
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
from enum import Enum


class PrimitiveType(Enum):
    """MCP Primitive Types"""
    TOOL = "tool"
    RESOURCE = "resource"
    PROMPT = "prompt"


@dataclass
class ToolParameter:
    """Tool Parameter Definition"""
    name: str
    type: str
    description: str
    required: bool = False
    default: Optional[Any] = None
    enum: Optional[List[str]] = None


@dataclass
class Tool:
    """MCP Tool Definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]
    parameters: List[ToolParameter] = field(default_factory=list)
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    deprecated: bool = False


@dataclass
class Resource:
    """MCP Resource Definition"""
    uri: str
    name: str
    description: str
    mimeType: Optional[str] = None
    size: Optional[int] = None
    lastModified: Optional[str] = None
    etag: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class PromptArgument:
    """MCP Prompt Argument"""
    name: str
    description: str
    type: str
    required: bool = False
    default: Optional[Any] = None
    validation: Optional[Dict[str, Any]] = None


@dataclass
class Prompt:
    """MCP Prompt Definition"""
    name: str
    description: str
    arguments: List[PromptArgument]
    template: str
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"


@dataclass
class Capability:
    """MCP Capability Definition"""
    type: PrimitiveType
    name: str
    description: str
    implementation: Union[Tool, Resource, Prompt]
    server: str
    domain: Optional[str] = None
    priority: int = 1
    enabled: bool = True


@dataclass
class ServerCapabilities:
    """Server Capabilities Collection"""
    server_name: str
    domain: str
    tools: List[Tool] = field(default_factory=list)
    resources: List[Resource] = field(default_factory=list)
    prompts: List[Prompt] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PrimitiveFactory:
    """Factory for creating MCP primitives"""
    
    @staticmethod
    def create_tool(name: str, description: str, parameters: List[Dict[str, Any]]) -> Tool:
        """Create a Tool from dictionary"""
        tool_params = []
        for param in parameters:
            tool_params.append(ToolParameter(
                name=param.get('name', ''),
                type=param.get('type', 'string'),
                description=param.get('description', ''),
                required=param.get('required', False),
                default=param.get('default'),
                enum=param.get('enum')
            ))
        
        return Tool(
            name=name,
            description=description,
            inputSchema={'type': 'object', 'properties': {}},
            parameters=tool_params
        )
    
    @staticmethod
    def create_resource(uri: str, name: str, description: str, **kwargs) -> Resource:
        """Create a Resource"""
        return Resource(
            uri=uri,
            name=name,
            description=description,
            **kwargs
        )
    
    @staticmethod
    def create_prompt(name: str, description: str, template: str, 
                     arguments: List[Dict[str, Any]]) -> Prompt:
        """Create a Prompt from dictionary"""
        prompt_args = []
        for arg in arguments:
            prompt_args.append(PromptArgument(
                name=arg.get('name', ''),
                description=arg.get('description', ''),
                type=arg.get('type', 'string'),
                required=arg.get('required', False),
                default=arg.get('default'),
                validation=arg.get('validation')
            ))
        
        return Prompt(
            name=name,
            description=description,
            template=template,
            arguments=prompt_args
        )


class PrimitiveValidator:
    """Validator for MCP primitives"""
    
    @staticmethod
    def validate_tool(tool: Tool) -> List[str]:
        """Validate a Tool definition"""
        errors = []
        
        if not tool.name:
            errors.append("Tool name is required")
        
        if not tool.description:
            errors.append("Tool description is required")
        
        if not tool.inputSchema:
            errors.append("Tool inputSchema is required")
        
        # Validate parameters
        for param in tool.parameters:
            if not param.name:
                errors.append("Parameter name is required")
            if not param.type:
                errors.append("Parameter type is required")
        
        return errors
    
    @staticmethod
    def validate_resource(resource: Resource) -> List[str]:
        """Validate a Resource definition"""
        errors = []
        
        if not resource.uri:
            errors.append("Resource URI is required")
        
        if not resource.name:
            errors.append("Resource name is required")
        
        if not resource.description:
            errors.append("Resource description is required")
        
        return errors
    
    @staticmethod
    def validate_prompt(prompt: Prompt) -> List[str]:
        """Validate a Prompt definition"""
        errors = []
        
        if not prompt.name:
            errors.append("Prompt name is required")
        
        if not prompt.description:
            errors.append("Prompt description is required")
        
        if not prompt.template:
            errors.append("Prompt template is required")
        
        # Validate arguments
        for arg in prompt.arguments:
            if not arg.name:
                errors.append("Argument name is required")
            if not arg.type:
                errors.append("Argument type is required")
        
        return errors
