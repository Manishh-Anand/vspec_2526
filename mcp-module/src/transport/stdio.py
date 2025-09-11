"""
Stdio Transport Implementation
"""

import asyncio
import json
import logging
import subprocess
from typing import Dict, Any, Optional, Union, AsyncGenerator
from .base import TransportLayer, TransportConfig


class StdioTransport(TransportLayer):
    """Stdio transport for MCP communication"""
    
    def __init__(self, config: TransportConfig, process: Optional[subprocess.Popen] = None):
        super().__init__(config)
        self.process = process
        self._next_id = 1
        self.logger = logging.getLogger(__name__)
        
    async def connect(self):
        """Connect to the stdio transport"""
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
            
            self.connected = True
            self.logger.info("Successfully connected to stdio transport")
            
        except Exception as e:
            self.logger.error(f"Error connecting to stdio transport: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from the stdio transport"""
        try:
            self.logger.info("Disconnecting from stdio transport")
            
            if self.process:
                if hasattr(self.process, 'terminate'):
                    # subprocess.Popen
                    self.process.terminate()
                    try:
                        # Use wait() without timeout for subprocess.Popen
                        self.process.wait()
                    except:
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
    
    async def send(self, data: Union[str, bytes]) -> bool:
        """Send data over stdio"""
        try:
            if not self.process or not self.process.stdin:
                return False
            
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            self.process.stdin.write(data)
            if hasattr(self.process.stdin, 'flush'):
                self.process.stdin.flush()
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending data: {e}")
            return False
    
    async def receive(self) -> Union[str, bytes]:
        """Receive data from stdio"""
        try:
            if not self.process or not self.process.stdout:
                raise ConnectionError("No process or stdout available")
            
            line = await self._read_response()
            if line:
                return line
            else:
                raise ConnectionError("No data received")
                
        except Exception as e:
            self.logger.error(f"Error receiving data: {e}")
            raise
    
    async def receive_stream(self) -> AsyncGenerator[Union[str, bytes], None]:
        """Receive data as stream from stdio"""
        try:
            if not self.process or not self.process.stdout:
                raise ConnectionError("No process or stdout available")
            
            while True:
                line = await self._read_response()
                if line:
                    yield line
                else:
                    break
                    
        except Exception as e:
            self.logger.error(f"Error in receive stream: {e}")
            raise
    
    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a JSON-RPC 2.0 request over stdio"""
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
            
            # Send request to stdin
            if self.process and self.process.stdin:
                # Check if stdin is text or binary
                if hasattr(self.process.stdin, 'encoding'):
                    # Text stream
                    self.process.stdin.write(request_json)
                else:
                    # Binary stream
                    self.process.stdin.write(request_json.encode('utf-8'))
                if hasattr(self.process.stdin, 'flush'):
                    self.process.stdin.flush()
                
                # Read response from stdout
                response_line = await self._read_response()
                if response_line:
                    response = json.loads(response_line)
                    return response
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request['id'],
                        "error": {
                            "code": -32603,
                            "message": "No response received from server"
                        }
                    }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request['id'],
                    "error": {
                        "code": -32603,
                        "message": "Process not available for communication"
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
    
    async def _read_response(self) -> Optional[str]:
        """Read response from stdout with timeout"""
        try:
            if not self.process or not self.process.stdout:
                return None
            
            # Read with timeout using proper async handling
            response_line = await asyncio.wait_for(
                self._read_line_async(),
                timeout=30.0
            )
            
            if response_line:
                return response_line.strip()
            else:
                return None
            
        except asyncio.TimeoutError:
            self.logger.error("Timeout reading response from server")
            return None
        except Exception as e:
            self.logger.error(f"Error reading response: {e}")
            return None
    
    async def _read_line_async(self) -> Optional[str]:
        """Read a line from stdout asynchronously"""
        try:
            if not self.process or not self.process.stdout:
                return None
            
            # Check if this is an asyncio.Process or subprocess.Popen
            if hasattr(self.process, 'stdout') and hasattr(self.process.stdout, 'readline'):
                # For subprocess.Popen, readline() is synchronous
                if hasattr(self.process.stdout, 'encoding'):
                    # Text stream
                    line = self.process.stdout.readline()
                    return line if line else None
                else:
                    # Binary stream
                    line = self.process.stdout.readline()
                    return line.decode('utf-8') if line else None
            else:
                # For asyncio.Process, readline() is a coroutine
                if hasattr(self.process.stdout, 'readline') and asyncio.iscoroutinefunction(self.process.stdout.readline):
                    line = await self.process.stdout.readline()
                    # Check if stdout is text or binary
                    if hasattr(self.process.stdout, 'encoding'):
                        # Text stream
                        return line if line else None
                    else:
                        # Binary stream
                        return line.decode('utf-8') if line else None
                else:
                    # Fallback: use run_in_executor for any blocking readline
                    loop = asyncio.get_event_loop()
                    line = await loop.run_in_executor(
                        None, 
                        self.process.stdout.readline
                    )
                    # Check if stdout is text or binary
                    if hasattr(self.process.stdout, 'encoding'):
                        # Text stream
                        return line if line else None
                    else:
                        # Binary stream
                        return line.decode('utf-8') if line else None
            
        except Exception as e:
            self.logger.error(f"Error reading line: {e}")
            return None
    
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
            
            # Send notification to stdin
            if self.process and self.process.stdin:
                # Check if stdin is text or binary
                if hasattr(self.process.stdin, 'encoding'):
                    # Text stream
                    self.process.stdin.write(notification_json)
                else:
                    # Binary stream
                    self.process.stdin.write(notification_json.encode('utf-8'))
                if hasattr(self.process.stdin, 'flush'):
                    self.process.stdin.flush()
                
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
    
    async def close(self):
        """Close the transport"""
        await self.disconnect()
