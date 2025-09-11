"""
Fixed HTTP Transport Implementation
HTTP transport with proper retry logic, connection pooling, and error handling
"""

import asyncio
import json
import logging
import aiohttp
import httpx
from typing import Dict, Any, Optional, Union, AsyncGenerator
from .base import TransportLayer, TransportConfig, TransportType, TransportError, ConnectionError, TimeoutError
from ..utils.error_handler import (
    get_global_async_error_handler, 
    TransportError as MCPTransportError,
    ConnectionError as MCPConnectionError,
    TimeoutError as MCPTimeoutError
)


class FixedHTTPTransport(TransportLayer):
    """Fixed HTTP transport with proper retry logic and connection handling"""
    
    def __init__(self, config: TransportConfig):
        super().__init__(config)
        self.session = None
        self.endpoint = config.endpoint
        self.headers = config.headers or {}
        self.auth_token = config.auth_token
        self.retry_count = 0
        self.max_retries = config.max_retries
        self.error_handler = get_global_async_error_handler()
        
        if self.auth_token:
            self.headers['Authorization'] = f'Bearer {self.auth_token}'
        
        self.headers['Content-Type'] = 'application/json'
        self.headers['User-Agent'] = 'MCP-Client/1.0'
    
    async def connect(self) -> bool:
        """Connect to HTTP transport with retry logic"""
        for attempt in range(self.max_retries + 1):
            try:
                self.logger.info(f"Connecting to HTTP transport: {self.endpoint} (attempt {attempt + 1})")
                
                # Ensure previous session is closed
                if self.session:
                    await self.session.close()
                    self.session = None
                
                # Create aiohttp session with proper configuration
                connector = aiohttp.TCPConnector(
                    limit=100,
                    limit_per_host=30,
                    ttl_dns_cache=300,
                    use_dns_cache=True,
                    keepalive_timeout=30,
                    enable_cleanup_closed=True
                )
                
                timeout = aiohttp.ClientTimeout(
                    total=self.config.timeout,
                    connect=5.0,
                    sock_read=10.0
                )
                
                self.session = aiohttp.ClientSession(
                    connector=connector,
                    headers=self.headers,
                    timeout=timeout,
                    raise_for_status=False
                )
                
                # Test connection with health check
                health_ok = await self._test_connection()
                if health_ok:
                    self.connected = True
                    self.retry_count = 0
                    self.logger.info("Successfully connected to HTTP transport")
                    return True
                else:
                    self.logger.warning(f"Health check failed on attempt {attempt + 1}")
                    
            except Exception as e:
                await self.error_handler.handle_async_error(
                    e, 
                    context={
                        "endpoint": self.endpoint,
                        "attempt": attempt + 1,
                        "max_retries": self.max_retries
                    }
                )
                
                # Always ensure session is closed on error
                if self.session:
                    try:
                        await self.session.close()
                    except Exception as close_error:
                        self.logger.debug(f"Error closing session: {close_error}")
                    finally:
                        self.session = None
                
                if attempt < self.max_retries:
                    wait_time = min(2 ** attempt, 10)  # Exponential backoff, max 10 seconds
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"Failed to connect after {self.max_retries + 1} attempts")
                    # Clean up session before returning
                    if self.session:
                        try:
                            await self.session.close()
                        except Exception as close_error:
                            self.logger.debug(f"Error closing session in final cleanup: {close_error}")
                        finally:
                            self.session = None
                    return False
        
        # Final cleanup if we failed to connect
        if self.session:
            try:
                await self.session.close()
            except Exception as close_error:
                self.logger.debug(f"Error closing session in final cleanup: {close_error}")
            finally:
                self.session = None
        
        return False
    
    async def _test_connection(self) -> bool:
        """Test connection with health check"""
        try:
            # Try multiple health check endpoints (prioritize MCP endpoint for FastMCP servers)
            health_endpoints = [
                f"{self.endpoint}/mcp",
                f"{self.endpoint}/health",
                f"{self.endpoint}/info"
            ]
            
            for endpoint in health_endpoints:
                try:
                    if endpoint.endswith('/mcp'):
                        # Use JSON-RPC 2.0 for MCP endpoints
                        init_request = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "initialize",
                            "params": {
                                "protocolVersion": "2024-11-05",
                                "capabilities": {},
                                "clientInfo": {"name": "mcp-client", "version": "1.0.0"}
                            }
                        }
                        async with self.session.post(
                            endpoint, 
                            json=init_request, 
                            headers={
                                "Accept": "application/json, text/event-stream",
                                "Content-Type": "application/json"
                            },
                            timeout=aiohttp.ClientTimeout(total=5.0)
                        ) as response:
                            if response.status in [200, 400]:  # 400 might be expected for some requests
                                self.logger.debug(f"Health check successful at {endpoint}: {response.status}")
                                return True
                    else:
                        # Use GET for other endpoints
                        async with self.session.get(endpoint, timeout=aiohttp.ClientTimeout(total=5.0)) as response:
                            if response.status in [200, 404, 405]:  # 404/405 are acceptable for some endpoints
                                self.logger.debug(f"Health check successful at {endpoint}: {response.status}")
                                return True
                except Exception as e:
                    self.logger.debug(f"Health check failed at {endpoint}: {e}")
                    continue
            
            # If no health check worked, try a simple MCP initialize request
            try:
                init_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "mcp-client", "version": "1.0.0"}
                    }
                }
                
                async with self.session.post(
                    f"{self.endpoint}/mcp",
                    json=init_request,
                    timeout=aiohttp.ClientTimeout(total=10.0)
                ) as response:
                    if response.status in [200, 400]:  # 400 might be expected for some requests
                        self.logger.debug(f"MCP endpoint accessible: {response.status}")
                        return True
            except Exception as e:
                self.logger.debug(f"MCP endpoint test failed: {e}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
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
        """Send data via HTTP with retry logic"""
        for attempt in range(self.max_retries + 1):
            try:
                if not self.connected:
                    if not await self.connect():
                        raise ConnectionError("Failed to establish connection")
                
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
                    f"{self.endpoint}/mcp",
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status == 200:
                        self.logger.debug(f"Sent data via HTTP: {data}")
                        return True
                    else:
                        error_text = await response.text()
                        self.logger.warning(f"HTTP send failed: {response.status} - {error_text}")
                        if attempt < self.max_retries:
                            await asyncio.sleep(2 ** attempt)
                            continue
                        return False
                        
            except Exception as e:
                self.logger.error(f"Error sending data via HTTP (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)
                    # Try to reconnect
                    await self.disconnect()
                    if not await self.connect():
                        continue
                else:
                    return False
        
        return False
    
    async def receive(self) -> Union[str, bytes]:
        """Receive data via HTTP"""
        try:
            if not self.connected:
                raise ConnectionError("Not connected to HTTP transport")
            
            # For HTTP, we typically don't "receive" in the traditional sense
            # This is more for compatibility with the interface
            return json.dumps({"status": "no_data", "message": "HTTP transport doesn't support receive"})
                    
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
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
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
    
    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a JSON-RPC 2.0 request via HTTP with proper error handling"""
        for attempt in range(self.max_retries + 1):
            try:
                if not self.connected:
                    if not await self.connect():
                        return {
                            "jsonrpc": "2.0",
                            "id": request.get('id', 0),
                            "error": {
                                "code": -32603,
                                "message": "Failed to establish connection"
                            }
                        }
                
                # Send POST request to MCP endpoint
                async with self.session.post(
                    f"{self.endpoint}/mcp",
                    json=request,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.logger.debug(f"HTTP request result: {result}")
                        return result
                    else:
                        error_text = await response.text()
                        self.logger.warning(f"HTTP request failed: {response.status} - {error_text}")
                        
                        if attempt < self.max_retries:
                            await asyncio.sleep(2 ** attempt)
                            continue
                        
                        return {
                            "jsonrpc": "2.0",
                            "id": request.get('id', 0),
                            "error": {
                                "code": -32603,
                                "message": f"HTTP request failed: {response.status} - {error_text}"
                            }
                        }
                        
            except asyncio.TimeoutError:
                self.logger.error(f"HTTP request timeout (attempt {attempt + 1})")
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return {
                    "jsonrpc": "2.0",
                    "id": request.get('id', 0),
                    "error": {
                        "code": -32603,
                        "message": "Request timeout"
                    }
                }
            except Exception as e:
                self.logger.error(f"Error sending HTTP request (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)
                    # Try to reconnect
                    await self.disconnect()
                    if not await self.connect():
                        continue
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get('id', 0),
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }
        
        return {
            "jsonrpc": "2.0",
            "id": request.get('id', 0),
            "error": {
                "code": -32603,
                "message": "Max retries exceeded"
            }
        }
    
    async def close(self):
        """Close the transport"""
        await self.disconnect()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the connection"""
        try:
            if not self.connected:
                return {"status": "disconnected", "error": "Not connected"}
            
            # Use JSON-RPC 2.0 for MCP health check
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "mcp-client", "version": "1.0.0"}
                }
            }
            
            async with self.session.post(
                f"{self.endpoint}/mcp",
                json=init_request,
                headers={
                    "Accept": "application/json, text/event-stream",
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=5.0)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {"status": "healthy", "data": data}
                else:
                    return {"status": "unhealthy", "status_code": response.status}
                    
        except Exception as e:
            return {"status": "error", "error": str(e)}


class HTTPTransportWithRetry:
    """HTTP Transport wrapper with enhanced retry logic using httpx"""
    
    def __init__(self, endpoint: str, timeout: float = 30.0, max_retries: int = 3):
        self.endpoint = endpoint
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
        
        # Create httpx client with proper configuration
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout, connect=5.0),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'MCP-Client/1.0'
            }
        )
    
    async def send_request_with_retry(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send request with exponential backoff retry logic"""
        for attempt in range(self.max_retries + 1):
            try:
                self.logger.debug(f"Sending request to {self.endpoint} (attempt {attempt + 1})")
                
                response = await self.client.post(
                    f"{self.endpoint}/mcp",
                    json=request,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.logger.debug(f"Request successful: {result}")
                    return result
                else:
                    error_text = response.text
                    self.logger.warning(f"Request failed: {response.status_code} - {error_text}")
                    
                    if attempt < self.max_retries:
                        wait_time = min(2 ** attempt, 10)
                        self.logger.info(f"Retrying in {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get('id', 0),
                        "error": {
                            "code": -32603,
                            "message": f"HTTP request failed: {response.status_code} - {error_text}"
                        }
                    }
                    
            except httpx.TimeoutException:
                self.logger.error(f"Request timeout (attempt {attempt + 1})")
                if attempt < self.max_retries:
                    wait_time = min(2 ** attempt, 10)
                    await asyncio.sleep(wait_time)
                    continue
                return {
                    "jsonrpc": "2.0",
                    "id": request.get('id', 0),
                    "error": {
                        "code": -32603,
                        "message": "Request timeout"
                    }
                }
            except httpx.ConnectError as e:
                self.logger.error(f"Connection error (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries:
                    wait_time = min(2 ** attempt, 10)
                    await asyncio.sleep(wait_time)
                    continue
                return {
                    "jsonrpc": "2.0",
                    "id": request.get('id', 0),
                    "error": {
                        "code": -32603,
                        "message": f"Connection error: {str(e)}"
                    }
                }
            except Exception as e:
                self.logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries:
                    wait_time = min(2 ** attempt, 10)
                    await asyncio.sleep(wait_time)
                    continue
                return {
                    "jsonrpc": "2.0",
                    "id": request.get('id', 0),
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
        
        return {
            "jsonrpc": "2.0",
            "id": request.get('id', 0),
            "error": {
                "code": -32603,
                "message": "Max retries exceeded"
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            # Use JSON-RPC 2.0 for MCP health check
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "mcp-client", "version": "1.0.0"}
                }
            }
            
            response = await self.client.post(
                f"{self.endpoint}/mcp",
                json=init_request,
                headers={
                    "Accept": "application/json, text/event-stream",
                    "Content-Type": "application/json"
                },
                timeout=5.0
            )
            
            if response.status_code == 200:
                return {"status": "healthy", "data": response.json()}
            else:
                return {"status": "unhealthy", "status_code": response.status_code}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def close(self):
        """Close the client"""
        await self.client.aclose()
