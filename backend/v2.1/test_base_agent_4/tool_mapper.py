# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# Tool Mapper - Maps abstract tools in BA_op.json to real MCP tools

# Flow:
# 1. Read BA_op.json
# 2. Extract all unique tool names from agents
# 3. Discover available MCP tools via Claude Code (one query)
# 4. Intelligently match abstract → real tool names
# 5. Output BA_enhanced.json with real tool mappings
# """

# import json
# import sys
# import subprocess
# import re
# from pathlib import Path
# from typing import Dict, List, Set, Tuple, Optional
# from datetime import datetime

# class ToolMapper:
#     """
#     Maps abstract tool names to real MCP tools available in Claude Code
#     """
    
#     def __init__(self, claude_cwd: Path = Path(r"C:\Users\manis")):
#         """
#         Initialize Tool Mapper
        
#         Args:
#             claude_cwd: Directory where Claude Code runs (where .claude.json lives)
#         """
#         self.claude_cwd = claude_cwd
#         self.timeout = 300  # seconds
#         self.discovered_tools = []  # List of real MCP tools
#         self.mapping = {}  # abstract_name → real_tool_info
#         self.unmapped_tools = []  # Tools that couldn't be mapped
        
#         # PowerShell command to run Claude Code
#         self.claude_cmd = [
#             "powershell.exe",
#             "-NoLogo",
#             "-NoProfile",
#             "-Command",
#             "claude"
#         ]
        
#         print("[INFO] Tool Mapper initialized")
#         print(f"[INFO] Claude Code directory: {self.claude_cwd}")
    
#     def process_ba_json(self, input_path: str, output_path: str = None) -> Dict:
#         """
#         Main process: Read BA_op.json, map tools, write BA_enhanced.json
        
#         Args:
#             input_path: Path to BA_op.json
#             output_path: Path for BA_enhanced.json (optional, defaults to same dir)
        
#         Returns:
#             Enhanced JSON structure
#         """
#         print("\n" + "="*60)
#         print("TOOL MAPPER - STARTING PROCESS")
#         print("="*60)
        
#         # Step 1: Read BA_op.json
#         print("\n[STEP 1] Reading BA_op.json...")
#         ba_data = self._read_json(input_path)
#         print(f"[INFO] Loaded workflow: {ba_data['workflow_metadata']['workflow_id']}")
#         print(f"   Domain: {ba_data['workflow_metadata']['domain']}")
#         print(f"   Agents: {ba_data['workflow_metadata']['total_agents']}")
        
#         # Step 2: Extract unique tool names
#         print("\n[STEP 2] Extracting abstract tool names...")
#         abstract_tools = self._extract_tool_names(ba_data)
#         print(f"[INFO] Found {len(abstract_tools)} unique tools:")
#         for tool in abstract_tools:
#             print(f"   - {tool}")
        
#         # Step 3: Discover real MCP tools
#         print("\n[STEP 3] Discovering MCP tools from Claude Code...")
#         self._discover_mcp_tools()
#         print(f"[INFO] Discovered {len(self.discovered_tools)} MCP tools")
        
#         # Step 4: Map abstract → real tools
#         print("\n[STEP 4] Mapping abstract tools to MCP tools...")
#         self._map_tools(abstract_tools)
#         print(f"[INFO] Mapped {len(self.mapping)} tools")
#         if self.unmapped_tools:
#             print(f"[WARN] Unmapped {len(self.unmapped_tools)} tools (will be marked)")
        
#         # Step 5: Enhance BA_op.json
#         print("\n[STEP 5] Creating BA_enhanced.json...")
#         enhanced_data = self._enhance_ba_json(ba_data)
        
#         # Step 6: Save output
#         if output_path is None:
#             # Save in same directory as input
#             input_file = Path(input_path)
#             output_path = input_file.parent / "BA_enhanced.json"
        
#         self._save_json(enhanced_data, output_path)
#         print(f"[SUCCESS] Saved to: {output_path}")
        
#         # Step 7: Print summary
#         self._print_summary()
        
#         return enhanced_data
    
#     def _read_json(self, file_path: str) -> Dict:
#         """Read and parse JSON file"""
#         try:
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#         except FileNotFoundError:
#             print(f"[ERROR] Error: File not found: {file_path}")
#             sys.exit(1)
#         except json.JSONDecodeError as e:
#             print(f"[ERROR] Error: Invalid JSON in {file_path}: {e}")
#             sys.exit(1)
    
#     def _extract_tool_names(self, ba_data: Dict) -> Set[str]:
#         """Extract all unique tool names from BA_op.json agents"""
#         tool_names = set()
        
#         for agent in ba_data.get('agents', []):
#             for tool in agent.get('tools', []):
#                 tool_name = tool.get('name', '').strip()
#                 if tool_name:
#                     tool_names.add(tool_name)
        
#         return tool_names
    
#     def _discover_mcp_tools(self) -> None:
#         """
#         Discover available MCP tools by querying Claude Code
#         Uses dynamic discovery - no hardcoding of servers
#         """
#         prompt = """List ALL your MCP servers and their available tools.

# For each server, provide:
# - Server name
# - Tool names (one per line)
# - What each tool does

# Format clearly like:
# Server: gmail
# - send_email: Send emails
# - list_emails: List inbox emails

# Server: github
# - create_repository: Create new repo
# - push_files: Push files to repo

# Include ALL servers. Be complete."""
        
#         print("  [INFO] Querying Claude Code for all MCP servers and tools...")
        
#         try:
#             response = self._call_claude_code(prompt)
            
#             # Parse response to extract tool names
#             tools = self._parse_tool_list(response)
#             self.discovered_tools = tools
            
#             if tools:
#                 # Count servers
#                 server_count = response.lower().count('server:')
#                 print(f"  [SUCCESS] Found {len(tools)} MCP tools from {server_count} servers:")
#                 for tool in tools[:10]:  # Show first 10
#                     print(f"     - {tool}")
#                 if len(tools) > 10:
#                     print(f"     ... and {len(tools)-10} more")
#             else:
#                 print("  [WARN] No tools found in Claude Code response")
#                 print(f"  Response preview: {response[:300]}...")
                
#         except Exception as e:
#             print(f"  [ERROR] Failed to discover tools: {e}")
#             self.discovered_tools = []
    
#     def _call_claude_code(self, prompt: str) -> str:
#         """
#         Call Claude Code via PowerShell and return response
        
#         Args:
#             prompt: Natural language prompt to send
            
#         Returns:
#             Claude Code's response text
#         """
#         try:
#             proc = subprocess.Popen(
#                 self.claude_cmd,
#                 cwd=str(self.claude_cwd),
#                 stdin=subprocess.PIPE,
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.STDOUT,
#                 text=True
#             )
            
#             stdout, _ = proc.communicate(prompt + "\n", timeout=self.timeout)
#             return stdout or ""
            
#         except subprocess.TimeoutExpired:
#             proc.kill()
#             raise TimeoutError(f"Claude Code took longer than {self.timeout} seconds")
#         except Exception as e:
#             raise RuntimeError(f"Failed to call Claude Code: {e}")
    
#     def _parse_tool_list(self, response: str) -> List[str]:
#         """
#         Parse Claude Code's response to extract tool names
        
#         Handles multiple formats:
#         1. "- **tool_name** - description" (Claude's natural format)
#         2. "- tool_name - description"
#         3. "* tool_name - description"
#         4. "1. tool_name - description"
#         5. Just "tool_name" on a line
#         6. "tool_name - description" without bullet
#         """
#         tools = []
#         lines = response.split('\n')
        
#         for line in lines:
#             line = line.strip()
#             if not line:
#                 continue
            
#             # Skip headers and section markers
#             if line.startswith('#') or line.startswith('##'):
#                 continue
#             if line.lower().startswith('server:') or line.lower().startswith('tools:'):
#                 continue
#             if line == '---' or line == '...':
#                 continue
            
#             # Pattern 1: "- **tool_name** - description" (Claude's rich format)
#             match = re.search(r'[-*]\s+\*\*([a-zA-Z0-9_-]+)\*\*', line)
#             if match:
#                 tool_name = match.group(1)
#                 if self._is_valid_tool_name(tool_name):
#                     tools.append(tool_name)
#                     continue
            
#             # Pattern 2: "- tool_name - description" or "- tool_name: description"
#             match = re.match(r'^[-*]\s+([a-zA-Z0-9_-]+)\s*[-:]', line)
#             if match:
#                 tool_name = match.group(1)
#                 if self._is_valid_tool_name(tool_name):
#                     tools.append(tool_name)
#                     continue
            
#             # Pattern 3: "1. tool_name - description" (numbered list)
#             match = re.match(r'^\d+\.\s+([a-zA-Z0-9_-]+)\s*[-:]', line)
#             if match:
#                 tool_name = match.group(1)
#                 if self._is_valid_tool_name(tool_name):
#                     tools.append(tool_name)
#                     continue
            
#             # Pattern 4: Just "- tool_name" (simple bullet)
#             match = re.match(r'^[-*]\s+([a-zA-Z0-9_-]+)$', line)
#             if match:
#                 tool_name = match.group(1)
#                 if self._is_valid_tool_name(tool_name):
#                     tools.append(tool_name)
#                     continue
            
#             # Pattern 5: "tool_name - something" or "tool_name: something" (no bullet)
#             match = re.match(r'^([a-zA-Z0-9_-]+)\s*[-:]', line)
#             if match:
#                 tool_name = match.group(1)
#                 if self._is_valid_tool_name(tool_name):
#                     tools.append(tool_name)
#                     continue
            
#             # Pattern 6: Just a word that looks like a tool name
#             if re.match(r'^[a-zA-Z0-9_-]+$', line):
#                 if self._is_valid_tool_name(line):
#                     tools.append(line)
        
#         # Remove duplicates while preserving order
#         seen = set()
#         unique_tools = []
#         for tool in tools:
#             if tool not in seen:
#                 seen.add(tool)
#                 unique_tools.append(tool)
        
#         return unique_tools
    
#     def _is_valid_tool_name(self, name: str) -> bool:
#         """
#         Check if a string looks like a valid tool name
        
#         Valid tool names:
#         - Contain letters, numbers, underscores, hyphens
#         - At least 3 characters
#         - Not common English words that appear in descriptions
#         """
#         if len(name) < 3:
#             return False
        
#         # Skip common words that aren't tool names
#         skip_words = {
#             'get', 'list', 'create', 'update', 'delete', 'add', 'remove',
#             'send', 'read', 'write', 'search', 'find', 'the', 'and', 'for',
#             'with', 'from', 'gmail', 'notion', 'github', 'email', 'calendar',
#             'repo', 'repository', 'issue', 'file', 'pull', 'request', 'tools',
#             'management', 'operations', 'platform', 'integration', 'support',
#             'workspace', 'user', 'team', 'members', 'details', 'info'
#         }
        
#         if name.lower() in skip_words:
#             return False
        
#         # Valid tool names usually have underscores or hyphens
#         # But not always (e.g., "getDiagnostics")
#         # So we'll be lenient here
#         return True
    
#     def _map_tools(self, abstract_tools: Set[str]) -> None:
#         """
#         Map abstract tool names to real MCP tools using intelligent matching
        
#         Strategy:
#         1. Skip 'general_tool' - it's a placeholder that needs replacement
#         2. Check if tool name already matches real MCP tool (exact match)
#         3. Try partial/semantic matching for other tools
#         4. Mark as unmapped if no match found
#         """
#         for abstract_name in abstract_tools:
#             # Special handling for general_tool - it's a placeholder
#             if abstract_name == "general_tool":
#                 print(f"  [WARN] {abstract_name} -> Placeholder (Base Agent needs better tool selection)")
#                 self.unmapped_tools.append(abstract_name)
#                 self.mapping[abstract_name] = {
#                     "real_name": abstract_name,
#                     "match_type": "placeholder",
#                     "confidence": "none",
#                     "warning": "This is a placeholder tool. Base Agent should provide specific tools."
#                 }
#                 continue
            
#             # Check if already a real tool (exact match in discovered tools)
#             if abstract_name in self.discovered_tools:
#                 self.mapping[abstract_name] = {
#                     "real_name": abstract_name,
#                     "match_type": "exact",
#                     "confidence": "high"
#                 }
#                 print(f"  [MATCH] {abstract_name} -> {abstract_name} (already correct!)")
#                 continue
            
#             # Try to find best match using semantic matching
#             real_tool = self._find_best_match(abstract_name)
            
#             if real_tool:
#                 self.mapping[abstract_name] = {
#                     "real_name": real_tool,
#                     "match_type": "matched",
#                     "confidence": "high"
#                 }
#                 print(f"  [MATCH] {abstract_name} -> {real_tool}")
#             else:
#                 # Mark as unmapped
#                 self.mapping[abstract_name] = {
#                     "real_name": abstract_name,  # Keep original
#                     "match_type": "unmapped",
#                     "confidence": "none"
#                 }
#                 self.unmapped_tools.append(abstract_name)
#                 print(f"  [WARN] {abstract_name} -> UNMAPPED (no MCP equivalent found)")
    
#     def _find_best_match(self, abstract_name: str) -> Optional[str]:
#         """
#         Find best matching MCP tool for an abstract tool name
        
#         Args:
#             abstract_name: Abstract tool name (e.g., "mail_retriever")
            
#         Returns:
#             Best matching MCP tool name or None
#         """
#         if not self.discovered_tools:
#             return None
        
#         abstract_lower = abstract_name.lower()
#         abstract_lower = abstract_lower.replace('_', ' ')  # Normalize underscores
        
#         # Strategy 1: Exact match (with normalization)
#         for tool in self.discovered_tools:
#             tool_normalized = tool.lower().replace('_', ' ').replace('-', ' ')
#             abstract_normalized = abstract_lower.replace(' ', '')
#             tool_no_spaces = tool_normalized.replace(' ', '')
            
#             if abstract_normalized == tool_no_spaces:
#                 return tool
        
#         # Strategy 2: Direct substring match
#         for tool in self.discovered_tools:
#             tool_lower = tool.lower()
#             if abstract_lower.replace(' ', '_') in tool_lower or abstract_lower.replace(' ', '-') in tool_lower:
#                 return tool
#             if tool_lower.replace('-', '_') in abstract_name.lower() or tool_lower.replace('_', '-') in abstract_name.lower():
#                 return tool
        
#         # Strategy 3: Keyword matching with scoring
#         abstract_keywords = set(abstract_lower.split())
#         best_match = None
#         best_score = 0
        
#         for tool in self.discovered_tools:
#             tool_normalized = tool.lower().replace('_', ' ').replace('-', ' ')
#             tool_keywords = set(tool_normalized.split())
            
#             # Calculate overlap score
#             overlap = len(abstract_keywords & tool_keywords)
            
#             # Bonus points for action words matching
#             action_words = {'send', 'get', 'list', 'create', 'update', 'delete', 'search', 'read', 'write', 'add', 'remove'}
#             action_overlap = len((abstract_keywords & action_words) & (tool_keywords & action_words))
            
#             total_score = overlap + (action_overlap * 0.5)
            
#             if total_score > best_score:
#                 best_score = total_score
#                 best_match = tool
        
#         # Only return if we have reasonable overlap
#         if best_score >= 1:
#             return best_match
        
#         # Strategy 4: Enhanced synonym matching
#         synonyms = {
#             'mail': ['email', 'message', 'gmail'],
#             'email': ['mail', 'message', 'gmail'],
#             'send': ['sender', 'compose', 'write'],
#             'retrieve': ['get', 'list', 'fetch', 'read'],
#             'get': ['retrieve', 'fetch', 'list', 'read'],
#             'create': ['add', 'new', 'make', 'write'],
#             'delete': ['remove', 'trash'],
#             'remove': ['delete', 'trash'],
#             'list': ['show', 'get', 'fetch'],
#             'search': ['find', 'query'],
#             'update': ['modify', 'edit', 'change'],
#             'schedule': ['calendar', 'event'],
#             'calendar': ['schedule', 'event'],
#             'repository': ['repo'],
#             'repo': ['repository'],
#             'summarize': ['summary'],
#             'summary': ['summarize'],
#             'research': ['search', 'scholar'],
#             'price': ['cost', 'comparison'],
#             'comparison': ['compare'],
#             'readme': ['documentation', 'doc'],
#             'link': ['url', 'share'],
#             'share': ['link', 'send']
#         }
        
#         for word in abstract_keywords:
#             if word in synonyms:
#                 for synonym in synonyms[word]:
#                     for tool in self.discovered_tools:
#                         tool_lower = tool.lower()
#                         if synonym in tool_lower:
#                             return tool
        
#         return None
    
#     def _enhance_ba_json(self, ba_data: Dict) -> Dict:
#         """
#         Create enhanced version of BA_op.json with real tool mappings
        
#         Args:
#             ba_data: Original BA_op.json data
            
#         Returns:
#             Enhanced JSON with real tool names
#         """
#         enhanced = json.loads(json.dumps(ba_data))  # Deep copy
        
#         # Update metadata
#         enhanced['workflow_metadata']['enhanced'] = True
#         enhanced['workflow_metadata']['enhanced_timestamp'] = datetime.now().isoformat()
#         enhanced['workflow_metadata']['mapping_stats'] = {
#             'total_tools': len(self.mapping),
#             'mapped': len(self.mapping) - len(self.unmapped_tools),
#             'unmapped': len(self.unmapped_tools)
#         }
        
#         # Update each agent's tools
#         for agent in enhanced.get('agents', []):
#             enhanced_tools = []
            
#             for tool in agent.get('tools', []):
#                 original_name = tool['name']
                
#                 if original_name in self.mapping:
#                     mapping_info = self.mapping[original_name]
                    
#                     enhanced_tool = tool.copy()
#                     enhanced_tool['name'] = mapping_info['real_name']
#                     enhanced_tool['original_name'] = original_name
#                     enhanced_tool['mapping_status'] = mapping_info['match_type']
#                     enhanced_tool['mapping_confidence'] = mapping_info['confidence']
                    
#                     # Add warnings based on mapping type
#                     if mapping_info['match_type'] == 'unmapped':
#                         enhanced_tool['warning'] = "No MCP equivalent found - using original name"
#                     elif mapping_info['match_type'] == 'placeholder':
#                         enhanced_tool['warning'] = mapping_info.get('warning', "Placeholder tool - needs replacement")
                    
#                     enhanced_tools.append(enhanced_tool)
#                 else:
#                     # Shouldn't happen, but keep original if mapping missing
#                     enhanced_tools.append(tool)
            
#             agent['tools'] = enhanced_tools
        
#         return enhanced
    
#     def _save_json(self, data: Dict, output_path: str) -> None:
#         """Save JSON to file"""
#         try:
#             output_path = Path(output_path)
#             output_path.parent.mkdir(parents=True, exist_ok=True)
            
#             with open(output_path, 'w', encoding='utf-8') as f:
#                 json.dump(data, f, indent=2, ensure_ascii=False)
                
#         except Exception as e:
#             print(f"[ERROR] Error saving JSON: {e}")
#             sys.exit(1)
    
#     def _print_summary(self) -> None:
#         """Print final summary of mapping process with detailed breakdown"""
#         print("\n" + "="*60)
#         print("TOOL MAPPING SUMMARY")
#         print("="*60)
        
#         total = len(self.mapping)
#         exact_matches = sum(1 for m in self.mapping.values() if m['match_type'] == 'exact')
#         semantic_matches = sum(1 for m in self.mapping.values() if m['match_type'] == 'matched')
#         placeholders = sum(1 for m in self.mapping.values() if m['match_type'] == 'placeholder')
#         unmapped = len(self.unmapped_tools) - placeholders  # Exclude placeholders from unmapped count
        
#         print(f"[INFO] Total Tools Processed: {total}")
#         print(f"   [MATCH] Exact Matches: {exact_matches} (tool names already correct)")
#         print(f"   [MATCH] Semantic Matches: {semantic_matches} (mapped to similar tools)")
#         print(f"   [WARN] Placeholders: {placeholders} (need specific tools from Base Agent)")
#         print(f"   [ERROR] Unmapped: {unmapped} (no MCP equivalent exists)")
        
#         if placeholders > 0:
#             print(f"\n[WARN] PLACEHOLDER TOOLS DETECTED:")
#             for tool, mapping in self.mapping.items():
#                 if mapping['match_type'] == 'placeholder':
#                     print(f"   - {tool}")
#             print("\n   [INFO] Action Required:")
#             print("      Base Agent is generating 'general_tool' placeholders.")
#             print("      This means Claude Code integration in Base Agent needs fixing.")
#             print("      Check if Claude Code is responding with actual tool names.")
        
#         if unmapped > 0:
#             print(f"\n[ERROR] UNMAPPED TOOLS ({unmapped}):")
#             for tool in self.unmapped_tools:
#                 if self.mapping.get(tool, {}).get('match_type') != 'placeholder':
#                     print(f"   - {tool}")
#             print("\n   These tools have no MCP server equivalent.")

# def main():
#     """Main execution"""
#     print("Tool Mapper - BA_op.json -> BA_enhanced.json")
#     print("="*60)
    
#     # Hardcoded paths
#     input_file = r"D:\final_yr_project_2526\backend\v2.1\test_base_agent_4\BA_op.json"
#     output_file = r"D:\final_yr_project_2526\backend\v2.1\test_base_agent_4\BA_enhanced.json"
    
#     print(f"[INFO] Input:  {input_file}")
#     print(f"[INFO] Output: {output_file}")
#     print()
    
#     # Initialize mapper
#     mapper = ToolMapper()
    
#     # Process
#     try:
#         result = mapper.process_ba_json(input_file, output_file)
#         print(f"\n[SUCCESS] Success! Enhanced JSON saved to: {output_file}")
        
#     except Exception as e:
#         print(f"\n[ERROR] Error: {e}")
#         import traceback
#         traceback.print_exc()
#         sys.exit(1)


# if __name__ == "__main__":
#     import time
#     from datetime import datetime
    
#     MODULE_NAME = "tool_mapper"
#     start_time = time.time()

#     main()

#     duration = time.time() - start_time
#     print(f"\n[TIMING] {MODULE_NAME}: {duration:.2f}s")

#     try:
#         import json
#         timing_entry = {
#             "module": MODULE_NAME,
#             "duration_seconds": round(duration, 2),
#             "timestamp": datetime.now().isoformat()
#         }
#         with open('timing_log.jsonl', 'a', encoding='utf-8') as f:
#             f.write(json.dumps(timing_entry) + '\n')
#     except Exception as e:
#         print(f"[WARNING] Could not save timing: {e}")


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool Mapper - Maps generic tools to MCP server tools
Uses Claude Code to intelligently map tools
Generates BA_enhanced.json and PRESERVES user_prompt
"""

import json
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════
# CLAUDE CODE WRAPPER FOR INTELLIGENT TOOL MAPPING
# ═══════════════════════════════════════════════════════════════════════════

class ClaudeCodeWrapper:
    """
    Wrapper to communicate with Claude Code for intelligent tool mapping
    """
    def __init__(self, claude_cwd: Path = None, timeout: int = 60):
        self.claude_cwd = claude_cwd or Path(r"C:\Users\manis")
        self.timeout = timeout
    
    def query_available_tools(self):
        """
        Ask Claude Code what MCP tools are available
        """
        prompt = """List all available MCP tools in the following format:
tool_name | description
tool_name | description

Be concise. Only list the tool names and brief descriptions."""
        
        try:
            result = self._execute_claude_command(prompt)
            return self._parse_tool_list(result)
        except Exception as e:
            print(f"[WARN] Could not query Claude for tools: {e}")
            return {}
    
    def map_tool_intelligently(self, tool_name: str, purpose: str, available_tools: list):
        """
        Use Claude Code to intelligently map a tool to MCP equivalent
        """
        tools_str = "\n".join([f"- {t}" for t in available_tools[:20]])  # Limit to 20 for context
        
        prompt = f"""Map this tool to the best MCP equivalent:

Tool Name: {tool_name}
Purpose: {purpose}

Available MCP Tools:
{tools_str}

Respond with ONLY the exact MCP tool name that best matches, or "NO_MATCH" if none fit.
Do not explain, just give the tool name."""
        
        try:
            result = self._execute_claude_command(prompt)
            mapped = result.strip().split('\n')[0].strip()
            
            if mapped and mapped != "NO_MATCH" and len(mapped) < 100:
                return mapped, "high", "claude_mapped"
            else:
                return tool_name, "none", "unmapped"
                
        except Exception as e:
            print(f"[WARN] Claude mapping failed for {tool_name}: {e}")
            return tool_name, "none", "unmapped"
    
    def _execute_claude_command(self, prompt: str) -> str:
        """
        Execute Claude Code command and return output
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        input_file = self.claude_cwd / f"tool_mapper_query_{timestamp}.txt"
        
        try:
            # Write prompt to file
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            
            # Execute Claude Code
            cmd = ["powershell.exe", "-NoLogo", "-NoProfile", "-Command", "claude"]
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.claude_cwd),
                text=True,
                encoding='utf-8'
            )
            
            # Read prompt from file and send to Claude
            with open(input_file, 'r', encoding='utf-8') as f:
                input_data = f.read()
            
            stdout, stderr = proc.communicate(input=input_data, timeout=self.timeout)
            
            return stdout.strip()
            
        except subprocess.TimeoutExpired:
            proc.kill()
            raise Exception(f"Claude Code timeout after {self.timeout}s")
        except Exception as e:
            raise Exception(f"Claude Code execution failed: {e}")
        finally:
            # Cleanup
            if input_file.exists():
                try:
                    input_file.unlink()
                except:
                    pass
    
    def _parse_tool_list(self, output: str) -> dict:
        """
        Parse Claude's tool list output into dictionary
        """
        tools = {}
        lines = output.split('\n')
        
        for line in lines:
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 2:
                    tool_name = parts[0].strip()
                    description = parts[1].strip()
                    tools[tool_name] = description
        
        return tools


# ═══════════════════════════════════════════════════════════════════════════
# STATIC MCP TOOL MAPPING DATABASE (FALLBACK)
# ═══════════════════════════════════════════════════════════════════════════

MCP_TOOL_MAP = {
    # Web/Research Tools
    "search_web": "brightdata-mcp__web_search",
    "web_search": "brightdata-mcp__web_search",
    "search": "brightdata-mcp__web_search",
    "google_search": "brightdata-mcp__web_search",
    "bing_search": "brightdata-mcp__web_search",
    
    "read_url": "jina-mcp-server__read_url",
    "fetch_url": "jina-mcp-server__read_url",
    "get_webpage": "jina-mcp-server__read_url",
    "scrape_page": "jina-mcp-server__read_url",
    
    # Email Tools
    "send_email": "gsuite-mcp__send_email",
    "email": "gsuite-mcp__send_email",
    "gmail_send": "gmail-mcp-local__send_email",
    "send_mail": "gsuite-mcp__send_email",
    
    "read_email": "gmail-mcp-local__read_email",
    "search_email": "gmail-mcp-local__search_email",
    "get_emails": "gmail-mcp-local__read_email",
    
    # Calendar Tools
    "create_event": "gsuite-mcp__create_event",
    "schedule": "gsuite-mcp__create_event",
    "calendar_event": "gsuite-mcp__create_event",
    "add_event": "gsuite-mcp__create_event",
    
    "list_events": "gsuite-mcp__list_events",
    "get_events": "gsuite-mcp__list_events",
    "show_calendar": "gsuite-mcp__list_events",
    
    # Document Tools
    "create_doc": "notionMCP__notion-create-pages",
    "notion_create": "notionMCP__notion-create-pages",
    "create_page": "notionMCP__notion-create-pages",
    "new_page": "notionMCP__notion-create-pages",
    
    "search_notion": "notionMCP__notion-search",
    "update_page": "notionMCP__notion-update-page",
    "append_blocks": "notionMCP__notion-append-blocks",
    
    # GitHub Tools
    "create_repo": "github__create_repository",
    "create_repository": "github__create_repository",
    "push_files": "github__push_files",
    "upload_files": "github__push_files",
    "create_issue": "github__create_issue",
    "create_pr": "github__create_pull_request",
    "get_file": "github__get_file_contents",
    
    # Scholar Tools
    "search_papers": "google-scholar__search_papers",
    "get_paper": "google-scholar__get_paper_details",
    "find_research": "google-scholar__search_papers",
}


def map_tool_to_mcp_static(tool_name):
    """
    Map a generic tool name to its MCP equivalent using static database
    Returns: (mcp_name, confidence, status)
    """
    tool_lower = tool_name.lower().strip()
    
    # Direct match
    if tool_lower in MCP_TOOL_MAP:
        return MCP_TOOL_MAP[tool_lower], "high", "matched"
    
    # Fuzzy match - check if tool name contains key words
    for key, mcp_tool in MCP_TOOL_MAP.items():
        if key in tool_lower or tool_lower in key:
            return mcp_tool, "medium", "fuzzy_matched"
    
    # No match found
    return tool_name, "none", "unmapped"


def enhance_workflow_with_mcp_tools(workflow_data, use_claude: bool = True):
    """
    Enhance workflow by mapping tools to MCP equivalents
    Uses Claude Code for intelligent mapping if available
    """
    print("[INFO] Mapping tools to MCP servers...")
    
    # Initialize Claude Code wrapper if requested
    claude_wrapper = None
    available_mcp_tools = []
    
    if use_claude:
        try:
            print("[INFO] Initializing Claude Code for intelligent mapping...")
            claude_wrapper = ClaudeCodeWrapper()
            
            # Query available tools from Claude
            print("[INFO] Querying Claude for available MCP tools...")
            available_tools_dict = claude_wrapper.query_available_tools()
            available_mcp_tools = list(available_tools_dict.keys())
            
            if available_mcp_tools:
                print(f"[SUCCESS] Claude returned {len(available_mcp_tools)} MCP tools")
            else:
                print("[WARN] Claude returned no tools, falling back to static mapping")
                claude_wrapper = None
        except Exception as e:
            print(f"[WARN] Could not initialize Claude Code: {e}")
            print("[INFO] Falling back to static tool mapping")
            claude_wrapper = None
    
    mapped_count = 0
    unmapped_count = 0
    total_tools = 0
    
    for agent in workflow_data.get('agents', []):
        agent_name = agent.get('agent_name', 'Unknown')
        print(f"\n[AGENT] Processing: {agent_name}")
        
        enhanced_tools = []
        
        for tool in agent.get('tools', []):
            total_tools += 1
            original_name = tool.get('name', '')
            purpose = tool.get('purpose', '')
            
            # Try Claude-based intelligent mapping first
            if claude_wrapper and available_mcp_tools:
                mcp_name, confidence, status = claude_wrapper.map_tool_intelligently(
                    original_name, 
                    purpose, 
                    available_mcp_tools
                )
            else:
                # Fallback to static mapping
                mcp_name, confidence, status = map_tool_to_mcp_static(original_name)
            
            enhanced_tool = {
                "name": mcp_name,
                "purpose": purpose,
                "original_name": original_name,
                "mapping_status": status,
                "mapping_confidence": confidence
            }
            
            if status in ["matched", "claude_mapped"]:
                print(f"   [OK] {original_name} -> {mcp_name} ({status})")
                mapped_count += 1
            elif status == "fuzzy_matched":
                print(f"   [~]  {original_name} -> {mcp_name} (fuzzy)")
                mapped_count += 1
            else:
                print(f"   [X]  {original_name} -> No MCP equivalent found")
                enhanced_tool["warning"] = "No MCP equivalent found - using original name"
                unmapped_count += 1
            
            enhanced_tools.append(enhanced_tool)
        
        agent['tools'] = enhanced_tools
    
    print(f"\n[SUMMARY] Tool Mapping:")
    print(f"   Total tools: {total_tools}")
    print(f"   Mapped: {mapped_count}")
    print(f"   Unmapped: {unmapped_count}")
    print(f"   Mapping method: {'Claude Code + Static' if claude_wrapper else 'Static only'}")
    
    return workflow_data, {
        "total_tools": total_tools,
        "mapped": mapped_count,
        "unmapped": unmapped_count,
        "method": "claude_code" if claude_wrapper else "static"
    }


def main():
    print("\n" + "="*70)
    print("[INFO] Tool Mapper - Intelligent MCP Tool Resolution")
    print("="*70 + "\n")
    
    # Check arguments
    if len(sys.argv) < 2:
        print("[ERROR] Usage: python tool_mapper.py <BA_op.json> [--no-claude]")
        print("        --no-claude: Skip Claude Code, use static mapping only")
        sys.exit(1)
    
    input_file = sys.argv[1]
    use_claude = "--no-claude" not in sys.argv
    
    # Load workflow
    print(f"[INFO] Loading workflow from: {input_file}")
    
    if not Path(input_file).exists():
        print(f"[ERROR] File not found: {input_file}")
        sys.exit(1)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        workflow_data = json.load(f)
    
    print(f"[SUCCESS] Loaded workflow")
    print(f"   Workflow ID: {workflow_data['workflow_metadata'].get('workflow_id', 'unknown')}")
    print(f"   Agents: {len(workflow_data['agents'])}")
    print(f"   User Prompt: {workflow_data['workflow_metadata'].get('user_prompt', 'N/A')[:50]}...")
    
    # Enhance with MCP tools
    enhanced_data, mapping_stats = enhance_workflow_with_mcp_tools(workflow_data, use_claude=use_claude)
    
    # ═══════════════════════════════════════════════════════════════════════
    # CREATE ENHANCED WORKFLOW - PRESERVE USER PROMPT (CRITICAL)
    # ═══════════════════════════════════════════════════════════════════════
    
    enhanced_workflow = {
        "workflow_metadata": {
            "workflow_id": workflow_data['workflow_metadata']['workflow_id'],
            "domain": workflow_data['workflow_metadata']['domain'],
            "selected_architecture": workflow_data['workflow_metadata']['selected_architecture'],
            "total_agents": len(workflow_data['agents']),
            # ─────────────────────────────────────────────────────────────
            # PRESERVE ORIGINAL USER PROMPT (CRITICAL FIX)
            # ─────────────────────────────────────────────────────────────
            "user_prompt": workflow_data['workflow_metadata'].get('user_prompt', ''),
            "star_formatted": workflow_data['workflow_metadata'].get('star_formatted', ''),
            "created_at": workflow_data['workflow_metadata'].get('created_at', ''),
            # ─────────────────────────────────────────────────────────────
            "enhanced": True,
            "enhanced_timestamp": datetime.now().isoformat(),
            "mapping_stats": mapping_stats
        },
        "agents": enhanced_data['agents'],
        "orchestration": workflow_data['orchestration']
    }
    
    # Save enhanced workflow
    output_file = "BA_enhanced.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enhanced_workflow, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"[SUCCESS] Generated BA_enhanced.json")
    print(f"{'='*70}")
    print(f"   File: {output_file}")
    print(f"   Total agents: {len(enhanced_workflow['agents'])}")
    print(f"   Tools mapped: {mapping_stats['mapped']}/{mapping_stats['total_tools']}")
    print(f"   Mapping method: {mapping_stats['method']}")
    print(f"   User prompt preserved: {bool(enhanced_workflow['workflow_metadata']['user_prompt'])}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    MODULE_NAME = "tool_mapper"
    start_time = time.time()
    
    main()
    
    duration = time.time() - start_time
    print(f"[TIMING] {MODULE_NAME}: {duration:.2f}s\n")
    
    try:
        timing_entry = {
            "module": MODULE_NAME,
            "duration_seconds": round(duration, 2),
            "timestamp": datetime.now().isoformat()
        }
        with open('timing_log.jsonl', 'a', encoding='utf-8') as f:
            f.write(json.dumps(timing_entry) + '\n')
    except Exception as e:
        print(f"[WARNING] Could not save timing: {e}")