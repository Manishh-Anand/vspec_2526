"""
Environment-based Configuration
Centralized configuration management for MCP module
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class Environment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "json"
    file_path: Optional[str] = None
    max_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = False


@dataclass
class LLMConfig:
    """LLM configuration"""
    endpoint: str = "http://localhost:11434/api/generate"
    model: str = "openhermes-2.5-mistral-7b"
    timeout: float = 30.0
    max_retries: int = 3
    temperature: float = 0.3
    max_tokens: int = 1500


@dataclass
class CacheConfig:
    """Cache configuration"""
    enabled: bool = True
    backend: str = "memory"  # memory, redis
    ttl: int = 3600  # 1 hour
    max_size: int = 1000
    redis_url: Optional[str] = None


@dataclass
class ServerConfig:
    """MCP Server configuration"""
    name: str
    domain: str
    transport: str = "stdio"
    endpoint: Optional[str] = None
    command: Optional[str] = None
    args: List[str] = field(default_factory=list)
    auth_token: Optional[str] = None
    timeout: float = 30.0
    max_retries: int = 3
    enabled: bool = True


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    enabled: bool = True
    metrics_port: int = 9090
    health_port: int = 8080
    tracing_enabled: bool = False
    jaeger_endpoint: Optional[str] = None
    prometheus_enabled: bool = True


@dataclass
class SecurityConfig:
    """Security configuration"""
    enable_tls: bool = False
    cert_file: Optional[str] = None
    key_file: Optional[str] = None
    ca_file: Optional[str] = None
    require_auth: bool = False
    allowed_origins: List[str] = field(default_factory=list)


@dataclass
class PerformanceConfig:
    """Performance configuration"""
    max_concurrent_requests: int = 100
    request_timeout: float = 30.0
    connection_pool_size: int = 10
    enable_compression: bool = True
    buffer_size: int = 8192


class MCPModuleSettings:
    """Main settings class for MCP module"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.environment = Environment(os.getenv("MCP_ENV", "development"))
        
        # Load configuration
        self._load_config()
        
        # Initialize sub-configurations
        self.logging = LoggingConfig(**self._config.get('logging', {}))
        self.llm = LLMConfig(**self._config.get('llm', {}))
        self.cache = CacheConfig(**self._config.get('cache', {}))
        self.monitoring = MonitoringConfig(**self._config.get('monitoring', {}))
        self.security = SecurityConfig(**self._config.get('security', {}))
        self.performance = PerformanceConfig(**self._config.get('performance', {}))
        
        # Load servers configuration
        self.servers = self._load_servers_config()
    
    def _get_default_config_path(self) -> str:
        """Get default configuration path"""
        base_path = Path(__file__).parent
        return str(base_path / "config.yaml")
    
    def _load_config(self) -> None:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self._config = yaml.safe_load(f) or {}
            else:
                self._config = self._get_default_config()
                self._save_config()
        except Exception as e:
            print(f"Warning: Failed to load config from {self.config_path}: {e}")
            self._config = self._get_default_config()
    
    def _save_config(self) -> None:
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False)
        except Exception as e:
            print(f"Warning: Failed to save config to {self.config_path}: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'environment': self.environment.value,
            'logging': {
                'level': 'INFO',
                'format': 'json',
                'enable_console': True,
                'enable_file': False
            },
            'llm': {
                'endpoint': 'http://localhost:11434/api/generate',
                'model': 'openhermes-2.5-mistral-7b',
                'timeout': 30.0,
                'max_retries': 3,
                'temperature': 0.3,
                'max_tokens': 1500
            },
            'cache': {
                'enabled': True,
                'backend': 'memory',
                'ttl': 3600,
                'max_size': 1000
            },
            'monitoring': {
                'enabled': True,
                'metrics_port': 9090,
                'health_port': 8080,
                'tracing_enabled': False,
                'prometheus_enabled': True
            },
            'security': {
                'enable_tls': False,
                'require_auth': False,
                'allowed_origins': []
            },
            'performance': {
                'max_concurrent_requests': 100,
                'request_timeout': 30.0,
                'connection_pool_size': 10,
                'enable_compression': True,
                'buffer_size': 8192
            }
        }
    
    def _load_servers_config(self) -> List[ServerConfig]:
        """Load servers configuration"""
        servers_config_path = Path(__file__).parent / "servers.yaml"
        
        try:
            if servers_config_path.exists():
                with open(servers_config_path, 'r') as f:
                    servers_data = yaml.safe_load(f) or {}
            else:
                servers_data = self._get_default_servers_config()
                self._save_servers_config(servers_data)
            
            servers = []
            for server_data in servers_data.get('servers', []):
                servers.append(ServerConfig(**server_data))
            
            return servers
            
        except Exception as e:
            print(f"Warning: Failed to load servers config: {e}")
            return []
    
    def _save_servers_config(self, config: Dict[str, Any]) -> None:
        """Save servers configuration"""
        try:
            servers_config_path = Path(__file__).parent / "servers.yaml"
            with open(servers_config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
        except Exception as e:
            print(f"Warning: Failed to save servers config: {e}")
    
    def _get_default_servers_config(self) -> Dict[str, Any]:
        """Get default servers configuration"""
        return {
            'servers': [
                {
                    'name': 'finance_server',
                    'domain': 'finance',
                    'transport': 'stdio',
                    'command': 'python',
                    'args': ['-m', 'mcp_servers.finance.server'],
                    'enabled': True
                },
                {
                    'name': 'productivity_server',
                    'domain': 'productivity',
                    'transport': 'http',
                    'endpoint': 'http://localhost:8001',
                    'enabled': True
                },
                {
                    'name': 'education_server',
                    'domain': 'education',
                    'transport': 'stdio',
                    'command': 'python',
                    'args': ['-m', 'mcp_servers.education.server'],
                    'enabled': True
                },
                {
                    'name': 'sports_server',
                    'domain': 'sports',
                    'transport': 'http',
                    'endpoint': 'http://localhost:8003',
                    'enabled': True
                },
                {
                    'name': 'software_dev_server',
                    'domain': 'software_dev',
                    'transport': 'stdio',
                    'command': 'python',
                    'args': ['-m', 'mcp_servers.software_dev.server'],
                    'enabled': True
                }
            ]
        }
    
    def get_server_config(self, name: str) -> Optional[ServerConfig]:
        """Get server configuration by name"""
        for server in self.servers:
            if server.name == name:
                return server
        return None
    
    def get_servers_by_domain(self, domain: str) -> List[ServerConfig]:
        """Get servers by domain"""
        return [server for server in self.servers if server.domain == domain]
    
    def get_enabled_servers(self) -> List[ServerConfig]:
        """Get all enabled servers"""
        return [server for server in self.servers if server.enabled]
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration"""
        self._config.update(updates)
        self._save_config()
        
        # Reload sub-configurations
        if 'logging' in updates:
            self.logging = LoggingConfig(**self._config.get('logging', {}))
        if 'llm' in updates:
            self.llm = LLMConfig(**self._config.get('llm', {}))
        if 'cache' in updates:
            self.cache = CacheConfig(**self._config.get('cache', {}))
        if 'monitoring' in updates:
            self.monitoring = MonitoringConfig(**self._config.get('monitoring', {}))
        if 'security' in updates:
            self.security = SecurityConfig(**self._config.get('security', {}))
        if 'performance' in updates:
            self.performance = PerformanceConfig(**self._config.get('performance', {}))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return {
            'environment': self.environment.value,
            'config_path': self.config_path,
            'logging': self.logging.__dict__,
            'llm': self.llm.__dict__,
            'cache': self.cache.__dict__,
            'monitoring': self.monitoring.__dict__,
            'security': self.security.__dict__,
            'performance': self.performance.__dict__,
            'servers': [server.__dict__ for server in self.servers]
        }


# Global settings instance
settings = MCPModuleSettings()
