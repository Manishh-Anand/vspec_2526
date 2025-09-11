"""
HTTP Transport Implementation
HTTP/SSE transport for MCP communication
"""

import asyncio
import json
import logging
import aiohttp
from typing import Dict, Any, Optional, Union, AsyncGenerator
from .base import TransportLayer, TransportConfig, TransportType, TransportError, ConnectionError, TimeoutError


class HTTPTransport(TransportLayer):
    """HTTP transport implementation"""
    
    def __init__(self, config: TransportConfig):
        super().__init__(config)
        self.session = None
        self.endpoint = config.endpoint
        self.headers = config.headers or {}
        self.auth_token = config.auth_token
        
        if self.auth_token:
            self.headers['Authorization'] = f'Bearer {self.auth_token}'
        
        self.headers['Content-Type'] = 'application/json'
    
    async def connect(self) -> bool:
        """Connect to HTTP transport"""
        try:
            self.logger.info(f"Connecting to HTTP transport: {self.endpoint}")
            
            # Create aiohttp session
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
            
            # Test connection with health check
            try:
                async with self.session.get(f"{self.endpoint}/health") as response:
                    if response.status == 200:
                        self.connected = True
                        self.logger.info("Successfully connected to HTTP transport")
                        return True
                    else:
                        self.logger.warning(f"Health check failed: {response.status}, but continuing...")
                        self.connected = True
                        return True
            except Exception as health_error:
                self.logger.warning(f"Health check failed: {health_error}, but continuing...")
                self.connected = True
                return True
                    
        except Exception as e:
            self.logger.error(f"Failed to connect to HTTP transport: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from HTTP transport"""
        try:
            self.logger.info("Disconnecting from HTTP transport")
            self.connected = False
            
            if self.session:
                await self.session.close()
                self.session = None
                
        except Exception as e:
            self.logger.error(f"Error disconnecting from HTTP transport: {e}")
    
    async def send(self, data: Union[str, bytes]) -> bool:
        """Send data via HTTP"""
        try:
            if not self.connected:
                raise ConnectionError("Not connected to HTTP transport")
            
            # Ensure data is dict for JSON
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    data = {"message": data}
            elif isinstance(data, bytes):
                data = {"message": data.decode('utf-8')}
            
            # Send POST request
            async with self.session.post(
                f"{self.endpoint}/message",
                json=data,
                timeout=self.config.timeout
            ) as response:
                if response.status == 200:
                    self.logger.debug(f"Sent data via HTTP: {data}")
                    return True
                else:
                    self.logger.error(f"HTTP send failed: {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error sending data via HTTP: {e}")
            return False
    
    async def receive(self) -> Union[str, bytes]:
        """Receive data via HTTP"""
        try:
            if not self.connected:
                raise ConnectionError("Not connected to HTTP transport")
            
            # Send GET request to receive message
            async with self.session.get(
                f"{self.endpoint}/message",
                timeout=self.config.timeout
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.logger.debug(f"Received data via HTTP: {data}")
                    return json.dumps(data)
                else:
                    raise ConnectionError(f"HTTP receive failed: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Error receiving data via HTTP: {e}")
            raise
    
    async def receive_stream(self) -> AsyncGenerator[Union[str, bytes], None]:
        """Receive data as stream via HTTP SSE"""
        try:
            if not self.connected:
                raise ConnectionError("Not connected to HTTP transport")
            
            async with self.session.get(
                f"{self.endpoint}/stream",
                timeout=self.config.timeout
            ) as response:
                if response.status == 200:
                    async for line in response.content:
                        if line:
                            data = line.decode('utf-8').strip()
                            if data.startswith('data: '):
                                data = data[6:]  # Remove 'data: ' prefix
                                try:
                                    json_data = json.loads(data)
                                    yield json.dumps(json_data)
                                except json.JSONDecodeError:
                                    yield data
                else:
                    raise ConnectionError(f"HTTP stream failed: {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Error in HTTP receive stream: {e}")
            raise
    
    async def send_json(self, data: Dict[str, Any]) -> bool:
        """Send JSON data via HTTP"""
        return await self.send(data)
    
    async def receive_json(self) -> Dict[str, Any]:
        """Receive JSON data via HTTP"""
        data = await self.receive()
        return json.loads(data)
    
    async def call_method(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Call a specific method via HTTP"""
        try:
            if not self.connected:
                raise ConnectionError("Not connected to HTTP transport")
            
            request_data = {
                "method": method,
                "params": params or {}
            }
            
            async with self.session.post(
                f"{self.endpoint}/rpc",
                json=request_data,
                timeout=self.config.timeout
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.debug(f"Method call result: {result}")
                    return result
                else:
                    error_text = await response.text()
                    raise ConnectionError(f"Method call failed: {response.status} - {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Error calling method via HTTP: {e}")
            raise
    
    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a JSON-RPC 2.0 request via HTTP"""
        try:
            if not self.connected:
                raise ConnectionError("Not connected to HTTP transport")
            
            # Send POST request to MCP endpoint
            async with self.session.post(
                f"{self.endpoint}/mcp",
                json=request,
                timeout=self.config.timeout
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.logger.debug(f"HTTP request result: {result}")
                    return result
                else:
                    error_text = await response.text()
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get('id', 0),
                        "error": {
                            "code": -32603,
                            "message": f"HTTP request failed: {response.status} - {error_text}"
                        }
                    }
                    
        except Exception as e:
            self.logger.error(f"Error sending HTTP request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get('id', 0),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def close(self):
        """Close the transport"""
        await self.disconnect()
