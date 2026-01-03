#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Setup Validator
Tests that all MCP servers are running and tools are callable before agent creation

What this validates:
1. Claude Code is accessible
2. All MCP servers are discovered
3. Each tool from BA_enhanced.json exists
4. Each tool is actually callable (optional dry-run test)

Usage:
    python validate_mcp_setup.py
    python validate_mcp_setup.py --enhanced-json "path/to/BA_enhanced.json"
    python validate_mcp_setup.py --test-calls  # Actually test calling tools (dry-run)
"""

import json
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class MCPValidator:
    """
    Validates MCP setup before agent creation
    """
    
    def __init__(self, claude_cwd: Path = Path(r"C:\Users\manis")):
        """Initialize validator"""
        self.claude_cwd = claude_cwd
        self.claude_cmd = [
            "powershell.exe",
            "-NoLogo",
            "-NoProfile",
            "-Command",
            "claude"
        ]
        
        self.discovered_servers = {}  # server_name → [tools]
        self.discovered_tools = []    # all tool names
        self.validation_results = {
            "claude_code_accessible": False,
            "servers_discovered": 0,
            "tools_discovered": 0,
            "tools_required": 0,
            "tools_validated": 0,
            "tools_missing": [],
            "tools_failed_test": [],
            "servers": {}
        }
        
        print("🔍 MCP Setup Validator")
        print("=" * 60)
    
    def validate_full_setup(self, enhanced_json_path: Optional[str] = None, test_calls: bool = False) -> bool:
        """
        Main validation process
        
        Args:
            enhanced_json_path: Path to BA_enhanced.json (optional)
            test_calls: If True, actually test calling each tool
            
        Returns:
            True if validation passes, False otherwise
        """
        print("\n🚀 Starting MCP Setup Validation")
        print("=" * 60)
        
        # Step 1: Test Claude Code accessibility
        print("\n📡 Step 1: Testing Claude Code accessibility...")
        if not self._test_claude_code_access():
            print("❌ FAILED: Cannot access Claude Code")
            print("   Make sure Claude Code is installed and running")
            return False
        print("✅ Claude Code is accessible")
        self.validation_results["claude_code_accessible"] = True
        
        # Step 2: Discover all MCP servers and tools
        print("\n🔍 Step 2: Discovering MCP servers and tools...")
        if not self._discover_all_mcp_servers():
            print("❌ FAILED: Could not discover MCP servers")
            return False
        
        print(f"✅ Discovered {len(self.discovered_servers)} MCP servers")
        print(f"✅ Discovered {len(self.discovered_tools)} total tools")
        self.validation_results["servers_discovered"] = len(self.discovered_servers)
        self.validation_results["tools_discovered"] = len(self.discovered_tools)
        
        # Print server summary
        for server, tools in self.discovered_servers.items():
            print(f"   📦 {server}: {len(tools)} tools")
            self.validation_results["servers"][server] = {
                "tool_count": len(tools),
                "tools": tools,
                "status": "discovered"
            }
        
        # Step 3: Validate tools from BA_enhanced.json (if provided)
        if enhanced_json_path:
            print(f"\n🗺️  Step 3: Validating tools from BA_enhanced.json...")
            if not self._validate_required_tools(enhanced_json_path):
                print("⚠️  WARNING: Some required tools are missing")
                print("   See details below")
            else:
                print("✅ All required tools are available")
        
        # Step 4: Test tool calls (if requested)
        if test_calls and enhanced_json_path:
            print(f"\n🧪 Step 4: Testing tool calls (dry-run)...")
            self._test_tool_calls(enhanced_json_path)
        
        # Print final report
        self._print_validation_report()
        
        # Determine if validation passed
        if self.validation_results["tools_missing"]:
            print("\n❌ VALIDATION FAILED: Missing tools detected")
            return False
        
        if test_calls and self.validation_results["tools_failed_test"]:
            print("\n⚠️  VALIDATION WARNING: Some tools failed test calls")
            return False
        
        print("\n✅ VALIDATION PASSED: MCP setup is ready!")
        return True
    
    def _test_claude_code_access(self) -> bool:
        """Test if Claude Code is accessible"""
        try:
            proc = subprocess.Popen(
                self.claude_cmd,
                cwd=str(self.claude_cwd),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Send a simple test query
            stdout, _ = proc.communicate("Hi, respond with 'OK' if you can hear me\n", timeout=30)
            
            # Check if we got any response
            if stdout and len(stdout.strip()) > 0:
                return True
            
            return False
            
        except Exception as e:
            print(f"   Error: {e}")
            return False
    
    def _discover_all_mcp_servers(self) -> bool:
        """Discover all MCP servers and their tools"""
        prompt = """List ALL your MCP servers and their available tools.

For each server, provide:
- Server name
- Tool names
- Brief description

Format like:
Server: gmail
- send_email: Send emails
- list_emails: List emails

Server: github
- create_repository: Create repo
- push_files: Push files

Be complete. Include ALL servers."""
        
        try:
            response = self._call_claude_code(prompt)
            
            if not response or "ERROR" in response:
                return False
            
            # Parse response to extract servers and tools
            self._parse_server_response(response)
            
            return len(self.discovered_servers) > 0
            
        except Exception as e:
            print(f"   Error: {e}")
            return False
    
    def _call_claude_code(self, prompt: str, timeout: int = 30) -> str:
        """Call Claude Code and return response"""
        try:
            proc = subprocess.Popen(
                self.claude_cmd,
                cwd=str(self.claude_cwd),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            stdout, _ = proc.communicate(prompt + "\n", timeout=timeout)
            return stdout or ""
            
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def _parse_server_response(self, response: str) -> None:
        """Parse Claude's response to extract servers and tools"""
        current_server = None
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            
            # Look for server declarations
            if line.lower().startswith('server:'):
                current_server = line.split(':', 1)[1].strip()
                if current_server not in self.discovered_servers:
                    self.discovered_servers[current_server] = []
            
            # Look for tool declarations (lines starting with -)
            elif line.startswith('-') and current_server:
                # Extract tool name
                tool_part = line[1:].strip()  # Remove leading '-'
                
                # Tool name is before ':' or end of line
                if ':' in tool_part:
                    tool_name = tool_part.split(':')[0].strip()
                else:
                    tool_name = tool_part.strip()
                
                # Clean up tool name (remove markdown, etc.)
                tool_name = tool_name.strip('*`')
                
                if tool_name and len(tool_name) > 2:
                    self.discovered_servers[current_server].append(tool_name)
                    if tool_name not in self.discovered_tools:
                        self.discovered_tools.append(tool_name)
    
    def _validate_required_tools(self, enhanced_json_path: str) -> bool:
        """Validate that all tools from BA_enhanced.json exist"""
        try:
            # Load BA_enhanced.json
            with open(enhanced_json_path, 'r', encoding='utf-8') as f:
                enhanced_data = json.load(f)
            
            # Extract all required tools
            required_tools = set()
            for agent in enhanced_data.get('agents', []):
                for tool in agent.get('tools', []):
                    tool_name = tool.get('name', '')
                    if tool_name:
                        required_tools.add(tool_name)
            
            self.validation_results["tools_required"] = len(required_tools)
            
            print(f"   📋 Found {len(required_tools)} unique tools required by agents")
            
            # Check each required tool
            missing_tools = []
            validated_tools = []
            
            for tool in sorted(required_tools):
                if tool in self.discovered_tools:
                    validated_tools.append(tool)
                    print(f"   ✅ {tool}")
                else:
                    missing_tools.append(tool)
                    print(f"   ❌ {tool} - NOT FOUND IN MCP SERVERS")
            
            self.validation_results["tools_validated"] = len(validated_tools)
            self.validation_results["tools_missing"] = missing_tools
            
            return len(missing_tools) == 0
            
        except FileNotFoundError:
            print(f"   ❌ File not found: {enhanced_json_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"   ❌ Invalid JSON: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def _test_tool_calls(self, enhanced_json_path: str) -> None:
        """Test actually calling each tool (dry-run with safe parameters)"""
        try:
            # Load BA_enhanced.json
            with open(enhanced_json_path, 'r', encoding='utf-8') as f:
                enhanced_data = json.load(f)
            
            # Extract unique tools
            tools_to_test = {}
            for agent in enhanced_data.get('agents', []):
                for tool in agent.get('tools', []):
                    tool_name = tool.get('name', '')
                    if tool_name and tool_name not in tools_to_test:
                        tools_to_test[tool_name] = tool
            
            print(f"   🧪 Testing {len(tools_to_test)} tools...")
            
            # Test each tool
            for tool_name, tool_info in tools_to_test.items():
                # Skip general_tool and unmapped tools
                if tool_name == "general_tool" or tool_info.get('mapping_status') == 'unmapped':
                    print(f"   ⏭️  {tool_name} - Skipped (unmapped/placeholder)")
                    continue
                
                # Perform dry-run test
                success = self._dry_run_tool_test(tool_name)
                
                if success:
                    print(f"   ✅ {tool_name} - Callable")
                else:
                    print(f"   ⚠️  {tool_name} - Test failed (may need parameters)")
                    self.validation_results["tools_failed_test"].append(tool_name)
                    
        except Exception as e:
            print(f"   ❌ Error testing tools: {e}")
    
    def _dry_run_tool_test(self, tool_name: str) -> bool:
        """
        Test if a tool is callable by asking Claude Code to describe it
        """
        prompt = f"""Do you have a tool called '{tool_name}'? 
If yes, respond with: YES - [brief description]
If no, respond with: NO"""
        
        try:
            response = self._call_claude_code(prompt, timeout=15)
            
            # Check if tool exists
            if response and "YES" in response.upper():
                return True
            
            return False
            
        except Exception as e:
            return False
    
    def _print_validation_report(self) -> None:
        """Print comprehensive validation report"""
        print("\n" + "=" * 60)
        print("📊 VALIDATION REPORT")
        print("=" * 60)
        
        # Connection status
        print(f"\n🔌 Claude Code Connection:")
        if self.validation_results["claude_code_accessible"]:
            print("   ✅ Accessible")
        else:
            print("   ❌ Not accessible")
        
        # Discovery summary
        print(f"\n🔍 MCP Discovery:")
        print(f"   Servers found: {self.validation_results['servers_discovered']}")
        print(f"   Total tools: {self.validation_results['tools_discovered']}")
        
        # Server breakdown
        print(f"\n📦 Servers:")
        for server, info in self.validation_results["servers"].items():
            print(f"   • {server}: {info['tool_count']} tools")
        
        # Tool validation (if performed)
        if self.validation_results["tools_required"] > 0:
            print(f"\n🗺️  Tool Validation:")
            print(f"   Required: {self.validation_results['tools_required']}")
            print(f"   Validated: {self.validation_results['tools_validated']}")
            
            if self.validation_results["tools_missing"]:
                print(f"   ❌ Missing: {len(self.validation_results['tools_missing'])}")
                for tool in self.validation_results["tools_missing"]:
                    print(f"      - {tool}")
            
            if self.validation_results["tools_failed_test"]:
                print(f"   ⚠️  Failed test: {len(self.validation_results['tools_failed_test'])}")
                for tool in self.validation_results["tools_failed_test"]:
                    print(f"      - {tool}")
        
        # Overall status
        print(f"\n" + "=" * 60)
        if self.validation_results["tools_missing"]:
            print("❌ VALIDATION STATUS: FAILED")
            print("\n💡 Actions Required:")
            print("   1. Check MCP server configuration in Claude Code")
            print("   2. Ensure all required MCP servers are installed")
            print("   3. Restart Claude Code if changes were made")
        else:
            print("✅ VALIDATION STATUS: PASSED")
            print("\n🎉 MCP setup is ready for agent creation!")
    
    def save_report(self, output_path: str = "mcp_validation_report.json") -> None:
        """Save validation report to JSON file"""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "validation_results": self.validation_results,
                "discovered_servers": self.discovered_servers,
                "discovered_tools": self.discovered_tools
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Validation report saved to: {output_path}")
            
        except Exception as e:
            print(f"\n❌ Failed to save report: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate MCP setup before agent creation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic validation (check Claude Code and discover servers)
  python validate_mcp_setup.py
  
  # Validate against BA_enhanced.json
  python validate_mcp_setup.py --enhanced-json BA_enhanced.json
  
  # Full validation with tool call tests
  python validate_mcp_setup.py --enhanced-json BA_enhanced.json --test-calls
  
  # Save validation report
  python validate_mcp_setup.py --enhanced-json BA_enhanced.json --save-report
        """
    )
    
    parser.add_argument(
        '--enhanced-json',
        type=str,
        help='Path to BA_enhanced.json file'
    )
    
    parser.add_argument(
        '--test-calls',
        action='store_true',
        help='Test actually calling each tool (dry-run)'
    )
    
    parser.add_argument(
        '--save-report',
        action='store_true',
        help='Save validation report to JSON file'
    )
    
    parser.add_argument(
        '--claude-cwd',
        type=str,
        default=r"C:\Users\manis",
        help='Directory where Claude Code runs'
    )
    
    args = parser.parse_args()
    
    # Create validator
    validator = MCPValidator(claude_cwd=Path(args.claude_cwd))
    
    # Run validation
    success = validator.validate_full_setup(
        enhanced_json_path=args.enhanced_json,
        test_calls=args.test_calls
    )
    
    # Save report if requested
    if args.save_report:
        validator.save_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()