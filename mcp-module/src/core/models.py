"""
Core data models for MCP module
"""

from dataclasses import dataclass
from typing import Any, Optional, List, Dict


@dataclass
class Tool:
    """MCP Tool model"""
    name: str
    description: str
    inputSchema: Dict[str, Any]


@dataclass
class Resource:
    """MCP Resource model"""
    uri: str
    name: str
    description: str
    mimeType: Optional[str] = None


@dataclass
class Prompt:
    """MCP Prompt model"""
    name: str
    description: str
    arguments: List[Any]


@dataclass
class ServerCapabilities:
    """MCP Server Capabilities model"""
    tools: List[Tool]
    resources: List[Resource]
    prompts: List[Prompt]


@dataclass
class MatchResult:
    """Result of a semantic matching operation"""
    tool: Any  # Can be Tool, Resource, or Prompt
    score: float
    confidence: float
    reasoning: str
    server: str
