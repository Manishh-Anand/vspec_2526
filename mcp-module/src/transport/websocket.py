"""
WebSocket Transport Implementation
WebSocket transport for MCP communication
"""

import asyncio
import json
import logging
import websockets
from typing import Dict, Any, Optional, Union, AsyncGenerator
from .base import TransportLayer, TransportConfig, TransportType, TransportError, ConnectionError, TimeoutError


class WebSocketTransport(TransportLayer):
    """WebSocket transport implementation"""
    
    def __init__(self, config: TransportConfig):
        super().__init__(config)
        self.websocket = None
        self.endpoint = config.endpoint
        self.headers = config.headers or {}
        self.auth_token = config.auth_token
        
        if self.auth_token:
            self.headers['Authorization'] = f'Bearer {self.auth_token}'
    
    async def connect(self) -> bool:
        """Connect to WebSocket transport"""
        try:
            self.logger.info(f"Connecting to WebSocket transport: {self.endpoint}")
            
            # Connect to WebSocket
            self.websocket = await websockets.connect(
                self.endpoint,
                extra_headers=self.headers,
                ping_interval=30,
                ping_timeout=10,
                close_timeout=10
            )
            
            self.connected = True
            self.logger.info("Successfully connected to WebSocket transport")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to WebSocket transport: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from WebSocket transport"""
        try:
            self.logger.info("Disconnecting from WebSocket transport")
            self.connected = False
            
            if self.websocket:
                await self.websocket.close()
                self.websocket = None
                
        except Exception as e:
            self.logger.error(f"Error disconnecting from WebSocket transport: {e}")
    
    async def send(self, data: Union[str, bytes]) -> bool:
        """Send data via WebSocket"""
        try:
            if not self.connected or not self.websocket:
                raise ConnectionError("Not connected to WebSocket transport")
            
            # Ensure data is string
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            elif isinstance(data, dict):
                data = json.dumps(data)
            
            await self.websocket.send(data)
            self.logger.debug(f"Sent data via WebSocket: {data}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending data via WebSocket: {e}")
            return False
    
    async def receive(self) -> Union[str, bytes]:
        """Receive data via WebSocket"""
        try:
            if not self.connected or not self.websocket:
                raise ConnectionError("Not connected to WebSocket transport")
            
            data = await self.websocket.recv()
            
            # Ensure data is string
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            
            self.logger.debug(f"Received data via WebSocket: {data}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error receiving data via WebSocket: {e}")
            raise
    
    async def receive_stream(self) -> AsyncGenerator[Union[str, bytes], None]:
        """Receive data as stream via WebSocket"""
        try:
            if not self.connected or not self.websocket:
                raise ConnectionError("Not connected to WebSocket transport")
            
            async for message in self.websocket:
                # Ensure data is string
                if isinstance(message, bytes):
                    message = message.decode('utf-8')
                
                self.logger.debug(f"Received stream data via WebSocket: {message}")
                yield message
                    
        except Exception as e:
            self.logger.error(f"Error in WebSocket receive stream: {e}")
            raise
    
    async def send_json(self, data: Dict[str, Any]) -> bool:
        """Send JSON data via WebSocket"""
        return await self.send(data)
    
    async def receive_json(self) -> Dict[str, Any]:
        """Receive JSON data via WebSocket"""
        data = await self.receive()
        return json.loads(data)
    
    async def ping(self) -> bool:
        """Send ping to WebSocket"""
        try:
            if not self.connected or not self.websocket:
                return False
            
            pong_waiter = await self.websocket.ping()
            await pong_waiter
            return True
            
        except Exception as e:
            self.logger.error(f"Error pinging WebSocket: {e}")
            return False
    
    async def is_alive(self) -> bool:
        """Check if WebSocket connection is alive"""
        try:
            if not self.connected or not self.websocket:
                return False
            
            return await self.ping()
            
        except Exception:
            return False
