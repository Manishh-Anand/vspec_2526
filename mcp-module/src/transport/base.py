"""
Transport Layer - Base Interface
Abstract transport interface for MCP communication
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, AsyncGenerator
from dataclasses import dataclass
from enum import Enum


class TransportType(Enum):
    """Transport Types"""
    STDIO = "stdio"
    HTTP = "http"
    WEBSOCKET = "websocket"


@dataclass
class TransportConfig:
    """Transport Configuration"""
    type: TransportType
    endpoint: Optional[str] = None
    timeout: float = 30.0
    max_retries: int = 3
    headers: Dict[str, str] = None
    auth_token: Optional[str] = None
    ssl_verify: bool = True
    buffer_size: int = 8192


class TransportError(Exception):
    """Base transport error"""
    pass


class ConnectionError(TransportError):
    """Connection error"""
    pass


class TimeoutError(TransportError):
    """Timeout error"""
    pass


class TransportLayer(ABC):
    """Abstract transport layer interface"""
    
    def __init__(self, config: TransportConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.connected = False
        self._connection_lock = asyncio.Lock()
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection"""
        pass
    
    @abstractmethod
    async def send(self, data: Union[str, bytes]) -> bool:
        """Send data"""
        pass
    
    @abstractmethod
    async def receive(self) -> Union[str, bytes]:
        """Receive data"""
        pass
    
    @abstractmethod
    async def receive_stream(self) -> AsyncGenerator[Union[str, bytes], None]:
        """Receive data as stream"""
        pass
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    def is_connected(self) -> bool:
        """Check if connected"""
        return self.connected
    
    async def ensure_connected(self) -> bool:
        """Ensure connection is established"""
        if not self.connected:
            async with self._connection_lock:
                if not self.connected:
                    return await self.connect()
        return self.connected
    
    async def send_with_retry(self, data: Union[str, bytes], max_retries: Optional[int] = None) -> bool:
        """Send data with retry logic"""
        max_retries = max_retries or self.config.max_retries
        
        for attempt in range(max_retries + 1):
            try:
                if not await self.ensure_connected():
                    raise ConnectionError("Failed to establish connection")
                
                return await self.send(data)
                
            except (ConnectionError, TimeoutError) as e:
                if attempt == max_retries:
                    self.logger.error(f"Failed to send data after {max_retries} attempts: {e}")
                    raise
                
                self.logger.warning(f"Send attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
                # Try to reconnect
                try:
                    await self.disconnect()
                    await self.connect()
                except Exception as reconnect_error:
                    self.logger.error(f"Reconnection failed: {reconnect_error}")
        
        return False
    
    async def receive_with_timeout(self, timeout: Optional[float] = None) -> Union[str, bytes]:
        """Receive data with timeout"""
        timeout = timeout or self.config.timeout
        
        try:
            return await asyncio.wait_for(self.receive(), timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Receive timeout after {timeout} seconds")


class TransportFactory:
    """Factory for creating transport layers"""
    
    _transports = {}
    
    @classmethod
    def register(cls, transport_type: TransportType, transport_class: type):
        """Register a transport implementation"""
        cls._transports[transport_type] = transport_class
    
    @classmethod
    def create(cls, config: TransportConfig) -> TransportLayer:
        """Create transport layer instance"""
        if config.type not in cls._transports:
            raise ValueError(f"Unsupported transport type: {config.type}")
        
        transport_class = cls._transports[config.type]
        return transport_class(config)
    
    @classmethod
    def create_from_dict(cls, config_dict: Dict[str, Any]) -> TransportLayer:
        """Create transport layer from dictionary configuration"""
        transport_type = TransportType(config_dict.get('type', 'stdio'))
        
        config = TransportConfig(
            type=transport_type,
            endpoint=config_dict.get('endpoint'),
            timeout=config_dict.get('timeout', 30.0),
            max_retries=config_dict.get('max_retries', 3),
            headers=config_dict.get('headers', {}),
            auth_token=config_dict.get('auth_token'),
            ssl_verify=config_dict.get('ssl_verify', True),
            buffer_size=config_dict.get('buffer_size', 8192)
        )
        
        return cls.create(config)


class TransportManager:
    """Manages multiple transport connections"""
    
    def __init__(self):
        self.transports: Dict[str, TransportLayer] = {}
        self.logger = logging.getLogger(__name__)
    
    async def add_transport(self, name: str, transport: TransportLayer) -> None:
        """Add transport to manager"""
        self.transports[name] = transport
        self.logger.info(f"Added transport: {name}")
    
    async def remove_transport(self, name: str) -> None:
        """Remove transport from manager"""
        if name in self.transports:
            transport = self.transports[name]
            await transport.disconnect()
            del self.transports[name]
            self.logger.info(f"Removed transport: {name}")
    
    async def get_transport(self, name: str) -> Optional[TransportLayer]:
        """Get transport by name"""
        return self.transports.get(name)
    
    async def send_to_transport(self, name: str, data: Union[str, bytes]) -> bool:
        """Send data to specific transport"""
        transport = await self.get_transport(name)
        if not transport:
            raise ValueError(f"Transport not found: {name}")
        
        return await transport.send_with_retry(data)
    
    async def broadcast(self, data: Union[str, bytes]) -> Dict[str, bool]:
        """Send data to all transports"""
        results = {}
        
        for name, transport in self.transports.items():
            try:
                results[name] = await transport.send_with_retry(data)
            except Exception as e:
                self.logger.error(f"Failed to send to transport {name}: {e}")
                results[name] = False
        
        return results
    
    async def close_all(self) -> None:
        """Close all transports"""
        for name, transport in self.transports.items():
            try:
                await transport.disconnect()
                self.logger.info(f"Closed transport: {name}")
            except Exception as e:
                self.logger.error(f"Error closing transport {name}: {e}")
        
        self.transports.clear()
    
    def get_connected_transports(self) -> Dict[str, TransportLayer]:
        """Get all connected transports"""
        return {
            name: transport 
            for name, transport in self.transports.items() 
            if transport.is_connected()
        }
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all transports"""
        health_status = {}
        
        for name, transport in self.transports.items():
            try:
                health_status[name] = transport.is_connected()
            except Exception as e:
                self.logger.error(f"Health check failed for {name}: {e}")
                health_status[name] = False
        
        return health_status
