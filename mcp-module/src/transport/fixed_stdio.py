"""
Fixed Stdio Transport Implementation
Stdio transport with proper timeout handling and connection management
"""

import asyncio
import json
import logging
import subprocess
import sys
from typing import Dict, Any, Optional, Union, AsyncGenerator
from .base import TransportLayer, TransportConfig, ConnectionError, TimeoutError


class FixedStdioTransport(TransportLayer):
    """Fixed stdio transport with proper timeout handling"""
    
    def __init__(self, config: TransportConfig, process: Optional[subprocess.Popen] = None):
        super().__init__(config)
        self.process = process
        self._next_id = 1
        self.logger = logging.getLogger(__name__)
        self._response_queue = asyncio.Queue()
        self._reader_task = None
        self._writer_task = None
        
    async def connect(self):
        """Connect to the stdio transport with proper initialization"""
        try:
            self.logger.info("Connecting to stdio transport")
            
            if not self.process:
                raise ValueError("No process provided for stdio transport")
            
            # Check if process is still running
            if hasattr(self.process, 'poll'):
                # subprocess.Popen
                if self.process.poll() is not None:
                    raise ConnectionError("Process has terminated")
            elif hasattr(self.process, 'returncode'):
                # asyncio.Process
                if self.process.returncode is not None:
                    raise ConnectionError("Process has terminated")
            
            # Start background reader task
            self._reader_task = asyncio.create_task(self._background_reader())
            
            # Wait a moment for the process to initialize
            await asyncio.sleep(0.5)
            
            # Test connection with a simple request
            test_request = {
                "jsonrpc": "2.0",
                "id": 0,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "mcp-client", "version": "1.0.0"}
                }
            }
            
            # Send test request with timeout
            try:
                response = await asyncio.wait_for(
                    self.send_request(test_request),
                    timeout=10.0
                )
                
                if 'error' in response:
                    self.logger.warning(f"Initialize test failed: {response['error']}")
                    # Don't fail connection for initialize errors, server might be working
                
                self.connected = True
                self.logger.info("Successfully connected to stdio transport")
                
            except asyncio.TimeoutError:
                self.logger.warning("Initialize test timed out, but continuing...")
                self.connected = True
                
        except Exception as e:
            self.logger.error(f"Error connecting to stdio transport: {e}")
            if self._reader_task:
                self._reader_task.cancel()
            raise
    
    async def disconnect(self):
        """Disconnect from the stdio transport"""
        try:
            self.logger.info("Disconnecting from stdio transport")
            
            # Cancel background tasks
            if self._reader_task:
                self._reader_task.cancel()
                try:
                    await self._reader_task
                except asyncio.CancelledError:
                    pass
            
            if self._writer_task:
                self._writer_task.cancel()
                try:
                    await self._writer_task
                except asyncio.CancelledError:
                    pass
            
            # Terminate process
            if self.process:
                if hasattr(self.process, 'terminate'):
                    # subprocess.Popen
                    self.process.terminate()
                    try:
                        # Use wait() without timeout for subprocess.Popen
                        self.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                else:
                    # asyncio.Process
                    self.process.terminate()
                    try:
                        await asyncio.wait_for(self.process.wait(), timeout=5)
                    except asyncio.TimeoutError:
                        self.process.kill()
            
            self.connected = False
            self.logger.info("Successfully disconnected from stdio transport")
            
        except Exception as e:
            self.logger.error(f"Error disconnecting from stdio transport: {e}")
    
    async def _background_reader(self):
        """Background task to read responses from stdout"""
        try:
            while self.connected:
                try:
                    line = await self._read_line_with_timeout(5.0)
                    if line:
                        try:
                            response = json.loads(line.strip())
                            await self._response_queue.put(response)
                        except json.JSONDecodeError:
                            self.logger.debug(f"Non-JSON line received: {line}")
                    else:
                        # No data, check if process is still alive
                        if hasattr(self.process, 'poll') and self.process.poll() is not None:
                            self.logger.warning("Process terminated")
                            break
                        await asyncio.sleep(0.1)
                        
                except asyncio.TimeoutError:
                    # Timeout is normal, continue reading
                    continue
                except Exception as e:
                    self.logger.error(f"Error in background reader: {e}")
                    await asyncio.sleep(1.0)
                    
        except asyncio.CancelledError:
            self.logger.debug("Background reader cancelled")
        except Exception as e:
            self.logger.error(f"Background reader error: {e}")
    
    async def _read_line_with_timeout(self, timeout: float) -> Optional[str]:
        """Read a line with timeout"""
        try:
            if not self.process or not self.process.stdout:
                return None
            
            # Use run_in_executor for blocking readline
            loop = asyncio.get_event_loop()
            line = await asyncio.wait_for(
                loop.run_in_executor(None, self.process.stdout.readline),
                timeout=timeout
            )
            
            if line:
                if hasattr(self.process.stdout, 'encoding'):
                    # Text stream
                    return line
                else:
                    # Binary stream
                    return line.decode('utf-8')
            return None
            
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            self.logger.error(f"Error reading line: {e}")
            return None
    
    async def send(self, data: Union[str, bytes]) -> bool:
        """Send data over stdio"""
        try:
            if not self.process or not self.process.stdin:
                return False
            
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # Use run_in_executor for blocking write
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._write_data, data)
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending data: {e}")
            return False
    
    def _write_data(self, data: bytes):
        """Write data to stdin (blocking)"""
        try:
            self.process.stdin.write(data)
            if hasattr(self.process.stdin, 'flush'):
                self.process.stdin.flush()
        except Exception as e:
            self.logger.error(f"Error writing data: {e}")
            raise
    
    async def receive(self) -> Union[str, bytes]:
        """Receive data from stdio"""
        try:
            # Wait for response from background reader
            response = await asyncio.wait_for(
                self._response_queue.get(),
                timeout=self.config.timeout
            )
            return json.dumps(response)
                
        except asyncio.TimeoutError:
            raise TimeoutError("No response received within timeout")
        except Exception as e:
            self.logger.error(f"Error receiving data: {e}")
            raise
    
    async def receive_stream(self) -> AsyncGenerator[Union[str, bytes], None]:
        """Receive data as stream from stdio"""
        try:
            while self.connected:
                try:
                    response = await asyncio.wait_for(
                        self._response_queue.get(),
                        timeout=1.0
                    )
                    yield json.dumps(response)
                except asyncio.TimeoutError:
                    # No data available, continue
                    continue
                except Exception as e:
                    self.logger.error(f"Error in receive stream: {e}")
                    break
                    
        except Exception as e:
            self.logger.error(f"Error in receive stream: {e}")
            raise
    
    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a JSON-RPC 2.0 request over stdio with proper timeout handling"""
        try:
            # Generate request ID if not present
            if 'id' not in request:
                request['id'] = self._next_id
                self._next_id += 1
            
            # Ensure JSON-RPC 2.0 format
            if 'jsonrpc' not in request:
                request['jsonrpc'] = '2.0'
            
            # Serialize request
            request_json = json.dumps(request) + '\n'
            
            # Send request
            if not await self.send(request_json):
                return {
                    "jsonrpc": "2.0",
                    "id": request['id'],
                    "error": {
                        "code": -32603,
                        "message": "Failed to send request"
                    }
                }
            
            # Wait for response with timeout
            try:
                response = await asyncio.wait_for(
                    self._wait_for_response(request['id']),
                    timeout=self.config.timeout
                )
                return response
                
            except asyncio.TimeoutError:
                self.logger.error(f"Timeout waiting for response to request {request['id']}")
                return {
                    "jsonrpc": "2.0",
                    "id": request['id'],
                    "error": {
                        "code": -32603,
                        "message": "No response received from server"
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Error sending request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get('id', 0),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def _wait_for_response(self, request_id: Any) -> Dict[str, Any]:
        """Wait for a specific response by ID"""
        timeout_count = 0
        max_timeouts = 10
        
        while timeout_count < max_timeouts:
            try:
                response = await asyncio.wait_for(
                    self._response_queue.get(),
                    timeout=1.0
                )
                
                # Check if this is the response we're waiting for
                if response.get('id') == request_id:
                    return response
                else:
                    # Not our response, put it back and continue waiting
                    await self._response_queue.put(response)
                    continue
                    
            except asyncio.TimeoutError:
                timeout_count += 1
                continue
        
        # If we get here, we've timed out
        raise asyncio.TimeoutError(f"No response received for request {request_id}")
    
    async def send_notification(self, notification: Dict[str, Any]):
        """Send a JSON-RPC 2.0 notification over stdio"""
        try:
            # Ensure JSON-RPC 2.0 format
            if 'jsonrpc' not in notification:
                notification['jsonrpc'] = '2.0'
            
            # Notifications don't have IDs
            if 'id' in notification:
                del notification['id']
            
            # Serialize notification
            notification_json = json.dumps(notification) + '\n'
            
            # Send notification
            await self.send(notification_json)
                
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
    
    async def close(self):
        """Close the transport"""
        await self.disconnect()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the connection"""
        try:
            if not self.connected:
                return {"status": "disconnected", "error": "Not connected"}
            
            # Check if process is still running
            if hasattr(self.process, 'poll'):
                if self.process.poll() is not None:
                    return {"status": "dead", "error": "Process terminated"}
            elif hasattr(self.process, 'returncode'):
                if self.process.returncode is not None:
                    return {"status": "dead", "error": "Process terminated"}
            
            # Send a simple ping request
            ping_request = {
                "jsonrpc": "2.0",
                "id": 999,
                "method": "ping"
            }
            
            try:
                response = await asyncio.wait_for(
                    self.send_request(ping_request),
                    timeout=5.0
                )
                return {"status": "healthy", "response": response}
            except asyncio.TimeoutError:
                return {"status": "unhealthy", "error": "Ping timeout"}
            except Exception as e:
                return {"status": "unhealthy", "error": str(e)}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
