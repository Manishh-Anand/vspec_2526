"""
Claude Code Wrapper - Real Working Implementation
Based on actual Claude Code behavior and config structure
"""

import subprocess
import json
import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClaudeCodeWrapper:
    """
    Wrapper to interact with Claude Code's MCP tools
    Uses config file parsing + natural language execution
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize wrapper
        Args:
            config_path: Path to .claude.json (auto-detected if not provided)
        """
        self.config_path = config_path or self._find_claude_config()
        self.tool_cache = {}
        self.servers_cache = None
        logger.info(f"🔧 Wrapper initialized with config: {self.config_path}")
    
    def _find_claude_config(self) -> str:
        """Auto-detect .claude.json location"""
        # Common locations
        possible_paths = [
            Path.home() / ".claude.json",
            Path("C:/Users/manis/.claude.json"),  # Your specific path
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        raise FileNotFoundError("Could not find .claude.json config file")
    
    def discover_tools(self) -> List[Dict[str, Any]]:
        """
        Discover all available MCP tools by:
        1. Parsing .claude.json for server configs
        2. Querying Claude Code for tool details
        """
        logger.info("🔍 Discovering tools...")
        
        # Parse config
        servers = self._parse_mcp_servers()
        
        if not servers:
            logger.warning("No MCP servers found in config")
            return []
        
        # For each server, get its tools
        all_tools = []
        for server_name, server_info in servers.items():
            logger.info(f"  Querying tools for: {server_name}")
            
            # Ask Claude Code about this server's tools
            tools = self._get_server_tools(server_name)
            
            for tool in tools:
                tool['server'] = server_name
                all_tools.append(tool)
        
        # Cache results
        self.servers_cache = servers
        logger.info(f"✅ Discovered {len(all_tools)} tools across {len(servers)} servers")
        
        return all_tools
    
    def _parse_mcp_servers(self) -> Dict[str, Dict]:
        """
        Parse .claude.json to extract MCP server configurations
        """
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Navigate to mcpServers section
            # Structure: {project_path: {mcpServers: {...}}}
            for key, value in config.items():
                # Skip if not a dict
                if not isinstance(value, dict):
                    continue
                    
                if 'mcpServers' in value:
                    servers = value['mcpServers']
                    logger.info(f"Found {len(servers)} MCP servers in config")
                    return servers
            
            logger.warning("No mcpServers found in config")
            return {}
            
        except Exception as e:
            logger.error(f"Failed to parse config: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _get_server_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """
        Get list of tools for a specific MCP server
        Uses natural language query to Claude Code
        """
        # Ask Claude Code to list tools for this server
        prompt = f"List all available tools for the {server_name} MCP server. Just list the tool names, one per line."
        
        try:
            response = self._call_claude_code(prompt)
            
            # Parse tool names from response
            tools = []
            lines = response.split('\n')
            
            for line in lines:
                line = line.strip()
                # Look for tool names (alphanumeric with underscores)
                tool_match = re.search(r'(\w+)', line)
                if tool_match and not line.startswith(('●', '-', 'The', 'I', 'Here')):
                    tool_name = tool_match.group(1)
                    tools.append({
                        'name': tool_name,
                        'description': line
                    })
            
            return tools
            
        except Exception as e:
            logger.warning(f"Could not get tools for {server_name}: {e}")
            # Return known tools based on your testing
            return self._get_known_tools(server_name)
    
    def _get_known_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """
        Fallback: Return known tools based on manual testing
        """
        known_tools = {
            'gsuite-mcp': [
                {'name': 'list_emails', 'description': 'List emails from Gmail'},
                {'name': 'search_emails', 'description': 'Search emails'},
                {'name': 'send_email', 'description': 'Send an email'},
                {'name': 'modify_email', 'description': 'Modify email'},
                {'name': 'list_events', 'description': 'List calendar events'},
                {'name': 'create_event', 'description': 'Create calendar event'},
                {'name': 'update_event', 'description': 'Update calendar event'},
                {'name': 'delete_event', 'description': 'Delete calendar event'},
            ],
            'github': [
                {'name': 'create_issue', 'description': 'Create GitHub issue'},
                {'name': 'add_comment', 'description': 'Add comment to issue'},
                {'name': 'create_branch', 'description': 'Create a branch'},
                {'name': 'create_file', 'description': 'Create or update file'},
            ],
            'formula1': [
                {'name': 'get_event_schedule', 'description': 'Get F1 event schedule'},
                {'name': 'get_event_info', 'description': 'Get event information'},
                {'name': 'get_session_results', 'description': 'Get session results'},
                {'name': 'get_driver_info', 'description': 'Get driver information'},
                {'name': 'analyze_driver_performance', 'description': 'Analyze driver performance'},
                {'name': 'compare_drivers', 'description': 'Compare drivers'},
                {'name': 'get_telemetry', 'description': 'Get telemetry data'},
                {'name': 'get_championship_standings', 'description': 'Get championship standings'},
            ],
            'notionMCP': [
                {'name': 'search', 'description': 'Search Notion'},
                {'name': 'create_page', 'description': 'Create Notion page'},
                {'name': 'update_page', 'description': 'Update Notion page'},
            ]
        }
        
        return known_tools.get(server_name, [])
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed schema for a tool
        Uses cached info or queries Claude Code
        """
        # Check cache
        if tool_name in self.tool_cache:
            return self.tool_cache[tool_name]
        
        logger.info(f"📖 Getting schema for: {tool_name}")
        
        # Ask Claude Code about this tool
        prompt = f"Describe the {tool_name} tool. What parameters does it accept?"
        
        try:
            response = self._call_claude_code(prompt)
            
            # Parse schema from response
            schema = {
                'name': tool_name,
                'description': response,
                'parameters': self._extract_parameters(response)
            }
            
            self.tool_cache[tool_name] = schema
            return schema
            
        except Exception as e:
            logger.error(f"Failed to get schema: {e}")
            return None
    
    def _extract_parameters(self, description: str) -> Dict[str, Any]:
        """
        Extract parameter information from tool description
        """
        params = {}
        
        # Look for parameter patterns
        # Example: "maxResults (number)", "subject (string, required)"
        param_patterns = [
            r'(\w+)\s*\(([^)]+)\)',  # param_name (type)
            r'- (\w+):?\s*([^\n]+)',  # - param_name: description
        ]
        
        for pattern in param_patterns:
            matches = re.findall(pattern, description)
            for match in matches:
                param_name = match[0]
                param_info = match[1]
                params[param_name] = {
                    'type': 'string',  # default
                    'description': param_info,
                    'required': 'required' in param_info.lower()
                }
        
        return params
    
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool using natural language
        This is how Claude Code actually works
        """
        logger.info(f"⚡ Executing: {tool_name}")
        logger.debug(f"   Parameters: {params}")
        
        # Build natural language prompt
        prompt = self._build_execution_prompt(tool_name, params)
        
        try:
            # Call Claude Code
            response = self._call_claude_code(prompt)
            
            # Parse response
            result = self._parse_execution_result(response)
            
            logger.info(f"✅ Tool {tool_name} completed")
            return {
                'success': True,
                'result': result,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"❌ Tool execution failed: {e}")
            return {
                'success': False,
                'result': None,
                'error': str(e)
            }
    
    def _build_execution_prompt(self, tool_name: str, params: Dict[str, Any]) -> str:
        """
        Build natural language prompt for tool execution
        Based on how Claude Code actually works
        """
        # Convert params to natural language
        param_str = ', '.join([f"{k}={v}" for k, v in params.items()])
        
        # Natural language prompt
        prompt = f"Use the {tool_name} tool"
        if params:
            prompt += f" with {param_str}"
        
        return prompt
    
    def _call_claude_code(self, prompt: str, timeout: int = 60) -> str:
        """
        Call Claude Code via subprocess with natural language prompt
        """
        try:
            # For Windows, use full command
            # Try different approaches
            commands_to_try = [
                ['npx', '-y', '@anthropic-ai/claude-code', 'chat', prompt],
                ['cmd', '/c', 'npx', '-y', '@anthropic-ai/claude-code', 'chat', prompt],
                ['claude', 'chat', prompt],  # If installed globally
            ]
            
            last_error = None
            for cmd in commands_to_try:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        cwd=str(Path.home())
                    )
                    
                    if result.returncode == 0:
                        return result.stdout.strip()
                    else:
                        last_error = result.stderr
                        continue
                        
                except FileNotFoundError:
                    continue
            
            raise Exception(f"Could not execute Claude Code. Last error: {last_error}")
                
        except subprocess.TimeoutExpired:
            raise Exception(f"Claude Code timed out after {timeout}s")
        except Exception as e:
            raise Exception(f"Failed to call Claude Code: {e}")
    
    def _parse_execution_result(self, response: str) -> Any:
        """
        Parse result from Claude Code response
        """
        # Look for JSON data
        json_match = re.search(r'\{[^{}]*\}|\[[^\[\]]*\]', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Look for structured data indicators
        if '●' in response:
            # Claude Code uses ● to mark tool outputs
            parts = response.split('●')
            if len(parts) > 1:
                return parts[1].strip()
        
        # Return cleaned text response
        return response.strip()


# Test code
if __name__ == "__main__":
    print("🧪 Testing Claude Code Wrapper")
    print("=" * 60)
    
    try:
        wrapper = ClaudeCodeWrapper()
        
        print("\n1️⃣ Discovering tools...")
        tools = wrapper.discover_tools()
        
        if tools:
            print(f"   Found {len(tools)} tools:")
            for tool in tools[:5]:
                print(f"   - {tool['name']} ({tool['server']})")
        
        print("\n2️⃣ Testing tool execution...")
        # Test with gsuite list_emails
        result = wrapper.execute_tool('list_emails', {'maxResults': 1})
        print(f"   Success: {result['success']}")
        if result['success']:
            print(f"   Result preview: {str(result['result'])[:100]}...")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")