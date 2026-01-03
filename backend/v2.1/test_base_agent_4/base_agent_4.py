# import requests
# import json
# import re
# import sys
# import time
# from pathlib import Path

# # LMStudioLLM Class (Copied from langchain_agentfactory.py)
# class LMStudioLLM:
#     def __init__(self, base_url="http://localhost:1234/v1", model="claude-3.7-sonnet-reasoning-gemma3-12b", temperature=0.3):
#         self.base_url = base_url
#         self.model = model
#         self.temperature = temperature
    
#     def invoke(self, messages):
#         if isinstance(messages, str):
#             messages = [{"role": "user", "content": messages}]
#         elif isinstance(messages, list) and len(messages) > 0:
#             if isinstance(messages[0], dict):
#                 pass
#             else:
#                 formatted = []
#                 for msg in messages:
#                     if hasattr(msg, 'type') and hasattr(msg, 'content'):
#                         role = "assistant" if msg.type == "ai" else "user"
#                         formatted.append({"role": role, "content": msg.content})
#                     else:
#                         formatted.append({"role": "user", "content": str(msg)})
#                 messages = formatted
        
#         payload = {
#             "model": self.model,
#             "messages": messages,
#             "temperature": self.temperature,
#             "max_tokens": 4000
#         }
        
#         response = requests.post(
#             f"{self.base_url}/chat/completions",
#             json=payload,
#             headers={"Content-Type": "application/json"}
#         )
#         response.raise_for_status()
#         result = response.json()
#         return {"content": result["choices"][0]["message"]["content"]}

# def extract_json_from_response(response_text):
#     """Extract JSON from LLM response with multiple fallback strategies"""
    
#     # Strategy 1: Try direct JSON parse
#     try:
#         return json.loads(response_text.strip())
#     except:
#         pass
    
#     # Strategy 2: Remove markdown code blocks
#     cleaned = re.sub(r'```json\s*|\s*```', '', response_text)
#     try:
#         return json.loads(cleaned.strip())
#     except:
#         pass
    
#     # Strategy 3: Find JSON object with regex
#     json_pattern = r'\{[\s\S]*\}'
#     matches = re.findall(json_pattern, response_text)
#     for match in matches:
#         try:
#             return json.loads(match)
#         except:
#             continue
    
#     # Strategy 4: Extract between first { and last }
#     start = response_text.find('{')
#     end = response_text.rfind('}')
#     if start != -1 and end != -1:
#         try:
#             return json.loads(response_text[start:end+1])
#         except:
#             pass
    
#     raise ValueError(f"Could not extract valid JSON from response: {response_text[:200]}...")

# def validate_ba_op_json(data):
#     """Validate that generated JSON has required structure"""
#     if 'workflow_metadata' not in data:
#         raise ValueError("Missing required key: workflow_metadata")
#     if 'agents' not in data:
#         raise ValueError("Missing required key: agents")
#     if 'orchestration' not in data:
#         raise ValueError("Missing required key: orchestration")
        
#     metadata = data['workflow_metadata']
#     required_meta = ['workflow_id', 'domain', 'selected_architecture']
#     for key in required_meta:
#         if key not in metadata:
#             raise ValueError(f"Missing required metadata key: {key}")
    
#     if not isinstance(data['agents'], list) or len(data['agents']) == 0:
#         raise ValueError("agents must be a non-empty list")
    
#     for i, agent in enumerate(data['agents']):
#         agent_required = ['agent_id', 'agent_name', 'position', 'identity', 'tools', 'interface']
#         for key in agent_required:
#             if key not in agent:
#                 raise ValueError(f"Agent {i} missing required key: {key}")
    
#     return True

# def main():
#     print("[INFO] Starting Base Agent 4...")
    
#     # Check LM Studio connection
#     try:
#         response = requests.get("http://localhost:1234/v1/models")
#         response.raise_for_status()
#         print("[SUCCESS] LM Studio is running")
#     except:
#         print("[ERROR] LM Studio not running! Start it and load Qwen model.")
#         sys.exit(1)

#     # Initialize LLM
#     llm = LMStudioLLM(
#         base_url="http://localhost:1234/v1",
#         model="claude-3.7-sonnet-reasoning-gemma3-12b",
#         temperature=0.3
#     )

#     # Read STAR input
#     star_file = Path(__file__).parent / "star_output.txt"
#     if not star_file.exists():
#         print(f"[ERROR] STAR output file not found: {star_file}")
#         print("Run system2starmethod.py first.")
#         sys.exit(1)
        
#     with open(star_file, 'r') as f:
#         star_formatted_prompt = f.read().strip()
        
#     print(f"[INFO] Read STAR prompt ({len(star_formatted_prompt)} chars)")

#     # Construct Prompt
#     prompt = f"""You are a workflow design AI. Your task is to create a multi-agent workflow based on the user's request.

# USER REQUEST (STAR FORMAT):
# {star_formatted_prompt}

# CRITICAL INSTRUCTIONS:
# 1. Analyze the request and determine what agents are needed
# 2. Each agent should have ONE specific job
# 3. Common agent types: ResearchAgent, AnalysisAgent, WriterAgent, NotifierAgent, DocumenterAgent, SchedulerAgent
# 4. Output ONLY valid JSON, nothing else
# 5. DO NOT include markdown code blocks, explanations, or commentary

# REQUIRED JSON STRUCTURE:
# {{
#   "workflow_metadata": {{
#     "workflow_id": "workflow_TIMESTAMP",
#     "domain": "Productivity|Research|Communication|Data|Creative",
#     "selected_architecture": "Pipeline/Sequential",
#     "total_agents": 2
#   }},
#   "agents": [
#     {{
#       "agent_id": "agent_1",
#       "agent_name": "**AgentName**",
#       "position": 1,
#       "identity": {{
#         "role": "One-line role description",
#         "description": "What this agent does"
#       }},
#       "tools": [
#         {{
#           "name": "search_web|send_email|create_doc|etc",
#           "purpose": "Why this tool is needed"
#         }}
#       ],
#       "interface": {{
#         "dependencies": [],
#         "outputs_to": ["agent_2"],
#         "error_strategy": "retry|skip|fail"
#       }}
#     }}
#   ],
#   "orchestration": {{
#     "pattern": "Pipeline/Sequential",
#     "connections": [
#       {{
#         "from": "agent_1",
#         "to": "agent_2",
#         "type": "sequential"
#       }}
#     ]
#   }}
# }}

# EXAMPLE for "Research electric cars and email me":
# {{
#   "workflow_metadata": {{
#     "workflow_id": "workflow_20241129_001",
#     "domain": "Research",
#     "selected_architecture": "Pipeline/Sequential",
#     "total_agents": 2
#   }},
#   "agents": [
#     {{
#       "agent_id": "agent_1",
#       "agent_name": "**ResearchAgent**",
#       "position": 1,
#       "identity": {{
#         "role": "Web Research Specialist",
#         "description": "Searches for information about electric cars"
#       }},
#       "tools": [
#         {{"name": "search_web", "purpose": "Find latest EV news"}},
#         {{"name": "read_url", "purpose": "Extract article content"}}
#       ],
#       "interface": {{
#         "dependencies": [],
#         "outputs_to": ["agent_2"],
#         "error_strategy": "retry"
#       }}
#     }},
#     {{
#       "agent_id": "agent_2",
#       "agent_name": "**NotifierAgent**",
#       "position": 2,
#       "identity": {{
#         "role": "Email Sender",
#         "description": "Sends research results via email"
#       }},
#       "tools": [
#         {{"name": "send_email", "purpose": "Send summary to user"}}
#       ],
#       "interface": {{
#         "dependencies": ["agent_1"],
#         "outputs_to": [],
#         "error_strategy": "retry"
#       }}
#     }}
#   ],
#   "orchestration": {{
#     "pattern": "Pipeline/Sequential",
#     "connections": [
#       {{
#         "from": "agent_1",
#         "to": "agent_2",
#         "type": "sequential"
#       }}
#     ]
#   }}
# }}

# NOW CREATE THE WORKFLOW JSON:
# """

#     # Generate Workflow
#     print("[INFO] Generating workflow...")
#     max_retries = 3
#     workflow_json = None
    
#     for attempt in range(max_retries):
#         try:
#             response = llm.invoke(prompt)
#             workflow_json = extract_json_from_response(response['content'])
#             validate_ba_op_json(workflow_json)
#             break
#         except Exception as e:
#             if attempt == max_retries - 1:
#                 print(f"[ERROR] Failed after {max_retries} attempts: {e}")
#                 sys.exit(1)
#             print(f"[WARN] Attempt {attempt + 1} failed: {e}, retrying...")
#             time.sleep(2)

#     # Save Output
#     output_path = Path(__file__).parent / "BA_op.json"
#     with open(output_path, 'w') as f:
#         json.dump(workflow_json, f, indent=2)

#     print(f"[SUCCESS] Generated BA_op.json successfully")
#     print(f"   Workflow ID: {workflow_json['workflow_metadata']['workflow_id']}")
#     print(f"   Domain: {workflow_json['workflow_metadata']['domain']}")
#     print(f"   Agents: {len(workflow_json['agents'])}")

# if __name__ == "__main__":
#     MODULE_NAME = "base_agent_4"
#     start_time = time.time()

#     main()

#     duration = time.time() - start_time
#     print(f"\n[TIMING] {MODULE_NAME}: {duration:.2f}s")

#     try:
#         import json
#         from datetime import datetime
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
Base Agent 4 - Workflow Generator
Generates BA_op.json with original user prompt preserved
"""

import requests
import json
import re
import sys
import time
import ast
from pathlib import Path
from datetime import datetime

# LMStudioLLM Class
class LMStudioLLM:
    def __init__(self, base_url="http://localhost:1234/v1", model="claude-3.7-sonnet-reasoning-gemma3-12b", temperature=0.3):
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
    
    def invoke(self, messages):
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        elif isinstance(messages, list) and len(messages) > 0:
            if isinstance(messages[0], dict):
                pass
            else:
                formatted = []
                for msg in messages:
                    if hasattr(msg, 'type') and hasattr(msg, 'content'):
                        role = "assistant" if msg.type == "ai" else "user"
                        formatted.append({"role": role, "content": msg.content})
                    else:
                        formatted.append({"role": "user", "content": str(msg)})
                messages = formatted
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": 4000
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        result = response.json()
        return {"content": result["choices"][0]["message"]["content"]}

def extract_json_from_response(response_text):
    """Extract JSON from LLM response with multiple fallback strategies"""
    
    # Strategy 1: Try direct JSON parse
    try:
        return json.loads(response_text.strip())
    except:
        pass
    
    # Strategy 2: Remove markdown code blocks
    cleaned = re.sub(r'```json\s*|\s*```', '', response_text)
    try:
        return json.loads(cleaned.strip())
    except:
        pass
    
    # Strategy 3: Find JSON object with regex
    json_pattern = r'\{[\s\S]*\}'
    matches = re.findall(json_pattern, response_text)
    for match in matches:
        try:
            return json.loads(match)
        except:
            continue
    
    # Strategy 4: Extract between first { and last }
    start = response_text.find('{')
    end = response_text.rfind('}')
    if start != -1 and end != -1:
        try:
            return json.loads(response_text[start:end+1])
        except:
            pass
    
    raise ValueError(f"Could not extract valid JSON from response: {response_text[:200]}...")

def validate_ba_op_json(data):
    """Validate that generated JSON has required structure"""
    if 'workflow_metadata' not in data:
        raise ValueError("Missing required key: workflow_metadata")
    if 'agents' not in data:
        raise ValueError("Missing required key: agents")
    if 'orchestration' not in data:
        raise ValueError("Missing required key: orchestration")
        
    metadata = data['workflow_metadata']
    required_meta = ['workflow_id', 'domain', 'selected_architecture']
    for key in required_meta:
        if key not in metadata:
            raise ValueError(f"Missing required metadata key: {key}")
    
    if not isinstance(data['agents'], list) or len(data['agents']) == 0:
        raise ValueError("agents must be a non-empty list")
    
    for i, agent in enumerate(data['agents']):
        agent_required = ['agent_id', 'agent_name', 'position', 'identity', 'tools', 'interface']
        for key in agent_required:
            if key not in agent:
                raise ValueError(f"Agent {i} missing required key: {key}")
    
    return True

def extract_original_prompt_from_star(star_text):
    """
    Extract the original user prompt from STAR formatted text
    """
    # Try to find the Situation section which usually contains the original request
    lines = star_text.split('\n')
    
    # Look for lines that seem like the original request
    original_prompt = None
    
    for i, line in enumerate(lines):
        # Check for common patterns
        if any(keyword in line.lower() for keyword in ['situation:', 'task:', 'user request:', 'objective:']):
            # Get the next non-empty line
            for j in range(i, min(i + 5, len(lines))):
                if lines[j].strip() and not lines[j].strip().endswith(':'):
                    original_prompt = lines[j].strip()
                    break
            if original_prompt:
                break
    
    # If not found, try to extract from the beginning
    if not original_prompt:
        for line in lines[:10]:  # Check first 10 lines
            stripped = line.strip()
            if stripped and len(stripped) > 20 and not stripped.endswith(':'):
                original_prompt = stripped
                break
    
    # Final fallback - use first substantial line
    if not original_prompt:
        for line in lines:
            stripped = line.strip()
            if len(stripped) > 20:
                original_prompt = stripped
                break
    
    return original_prompt or "Execute the workflow as designed"

def main():
    print("[INFO] Starting Base Agent 4 - Workflow Generator...")
    print("="*70)
    
    # Check LM Studio connection
    try:
        response = requests.get("http://localhost:1234/v1/models")
        response.raise_for_status()
        print("[SUCCESS] LM Studio is running")
    except:
        print("[ERROR] LM Studio not running! Start it and load Qwen model.")
        sys.exit(1)

    # Initialize LLM
    llm = LMStudioLLM(
        base_url="http://localhost:1234/v1",
        model="claude-3.7-sonnet-reasoning-gemma3-12b",
        temperature=0.3
    )

    # ═══════════════════════════════════════════════════════════════════════
    # READ ORIGINAL USER PROMPT FROM PYTHON FILES
    # ═══════════════════════════════════════════════════════════════════════
    
    original_user_prompt = None
    star_formatted_prompt = None
    
    # Strategy 1: Read from System_prompt.py (Python variable)
    system_prompt_file = Path(r"D:\final_yr_project_2526\backend\v2.1") / "System_prompt.py"
    
    if system_prompt_file.exists():
        print(f"[INFO] Reading original prompt from System_prompt.py")
        try:
            with open(system_prompt_file, 'r', encoding='utf-8') as f:
                code = f.read()
                tree = ast.parse(code)
                for node in tree.body:
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if hasattr(target, 'id') and target.id == "system_prompt":
                                original_user_prompt = ast.literal_eval(node.value)
                                break
                        if original_user_prompt:
                            break
            
            if original_user_prompt:
                print(f"[SUCCESS] Found original user prompt")
                print(f"[PROMPT] {original_user_prompt[:100]}...")
            else:
                print(f"[WARN] Could not find 'system_prompt' variable in System_prompt.py")
        except Exception as e:
            print(f"[WARN] Error reading System_prompt.py: {e}")
    else:
        print(f"[WARN] System_prompt.py not found at: {system_prompt_file}")
    
    # Strategy 2: Read STAR format from star_m.py (Python variable)
    star_file = Path(r"D:\final_yr_project_2526\backend\v2.1") / "star_m.py"
    
    if star_file.exists():
        print(f"[INFO] Reading STAR format from star_m.py")
        try:
            with open(star_file, 'r', encoding='utf-8') as f:
                code = f.read()
                tree = ast.parse(code)
                for node in tree.body:
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if hasattr(target, 'id') and target.id == "star_output":
                                star_formatted_prompt = ast.literal_eval(node.value)
                                break
                        if star_formatted_prompt:
                            break
            
            if star_formatted_prompt:
                print(f"[SUCCESS] Found STAR formatted prompt ({len(star_formatted_prompt)} characters)")
            else:
                print(f"[ERROR] Could not find 'star_output' variable in star_m.py")
                sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Error reading star_m.py: {e}")
            sys.exit(1)
    else:
        print(f"[ERROR] star_m.py not found at: {star_file}")
        print("[INFO] Run system_2_starMethod.py first.")
        sys.exit(1)
    
    # Strategy 3: If no original prompt, extract from STAR
    if not original_user_prompt and star_formatted_prompt:
        print(f"[INFO] Extracting original prompt from STAR format")
        original_user_prompt = extract_original_prompt_from_star(star_formatted_prompt)
        print(f"[PROMPT] {original_user_prompt[:100]}...")
    
    # Validate we have both
    if not original_user_prompt:
        print(f"[ERROR] Could not find original user prompt")
        sys.exit(1)
    
    if not star_formatted_prompt:
        print(f"[ERROR] Could not find STAR formatted prompt")
        sys.exit(1)
    
    print(f"\n{'='*70}")
    print(f"[SUCCESS] Loaded prompts successfully")
    print(f"   Original prompt: {len(original_user_prompt)} characters")
    print(f"   STAR format: {len(star_formatted_prompt)} characters")
    print(f"{'='*70}\n")

    # Construct Prompt
    prompt = f"""You are a workflow design AI. Your task is to create a multi-agent workflow based on the user's request.

USER REQUEST (STAR FORMAT):
{star_formatted_prompt}

CRITICAL INSTRUCTIONS:
1. Analyze the request and determine what agents are needed
2. Each agent should have ONE specific job
3. Common agent types: ResearchAgent, AnalysisAgent, WriterAgent, NotifierAgent, DocumenterAgent, SchedulerAgent
4. Output ONLY valid JSON, nothing else
5. DO NOT include markdown code blocks, explanations, or commentary

REQUIRED JSON STRUCTURE:
{{
  "workflow_metadata": {{
    "workflow_id": "workflow_TIMESTAMP",
    "domain": "Productivity|Research|Communication|Data|Creative",
    "selected_architecture": "Pipeline/Sequential",
    "total_agents": 2
  }},
  "agents": [
    {{
      "agent_id": "agent_1",
      "agent_name": "**AgentName**",
      "position": 1,
      "identity": {{
        "role": "One-line role description",
        "description": "What this agent does"
      }},
      "tools": [
        {{
          "name": "search_web|send_email|create_doc|etc",
          "purpose": "Why this tool is needed"
        }}
      ],
      "interface": {{
        "dependencies": [],
        "outputs_to": ["agent_2"],
        "error_strategy": "retry|skip|fail"
      }}
    }}
  ],
  "orchestration": {{
    "pattern": "Pipeline/Sequential",
    "connections": [
      {{
        "from": "agent_1",
        "to": "agent_2",
        "type": "sequential"
      }}
    ]
  }}
}}

EXAMPLE for "Research electric cars and email me":
{{
  "workflow_metadata": {{
    "workflow_id": "workflow_20241129_001",
    "domain": "Research",
    "selected_architecture": "Pipeline/Sequential",
    "total_agents": 2
  }},
  "agents": [
    {{
      "agent_id": "agent_1",
      "agent_name": "**ResearchAgent**",
      "position": 1,
      "identity": {{
        "role": "Web Research Specialist",
        "description": "Searches for information about electric cars"
      }},
      "tools": [
        {{"name": "search_web", "purpose": "Find latest EV news"}},
        {{"name": "read_url", "purpose": "Extract article content"}}
      ],
      "interface": {{
        "dependencies": [],
        "outputs_to": ["agent_2"],
        "error_strategy": "retry"
      }}
    }},
    {{
      "agent_id": "agent_2",
      "agent_name": "**NotifierAgent**",
      "position": 2,
      "identity": {{
        "role": "Email Sender",
        "description": "Sends research results via email"
      }},
      "tools": [
        {{"name": "send_email", "purpose": "Send summary to user"}}
      ],
      "interface": {{
        "dependencies": ["agent_1"],
        "outputs_to": [],
        "error_strategy": "retry"
      }}
    }}
  ],
  "orchestration": {{
    "pattern": "Pipeline/Sequential",
    "connections": [
      {{
        "from": "agent_1",
        "to": "agent_2",
        "type": "sequential"
      }}
    ]
  }}
}}

NOW CREATE THE WORKFLOW JSON:
"""

    # Generate Workflow
    print("[INFO] Generating workflow with LLM...")
    max_retries = 3
    workflow_json = None
    
    for attempt in range(max_retries):
        try:
            response = llm.invoke(prompt)
            workflow_json = extract_json_from_response(response['content'])
            validate_ba_op_json(workflow_json)
            print(f"[SUCCESS] Workflow JSON generated and validated")
            break
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"[ERROR] Failed after {max_retries} attempts: {e}")
                sys.exit(1)
            print(f"[WARN] Attempt {attempt + 1} failed: {e}")
            print(f"[INFO] Retrying in 2 seconds...")
            time.sleep(2)

    # ═══════════════════════════════════════════════════════════════════════
    # ADD ORIGINAL USER PROMPT TO WORKFLOW METADATA (CRITICAL FIX)
    # This allows agents to know what the actual user task is
    # ═══════════════════════════════════════════════════════════════════════
    
    workflow_json['workflow_metadata']['user_prompt'] = original_user_prompt
    workflow_json['workflow_metadata']['star_formatted'] = star_formatted_prompt
    workflow_json['workflow_metadata']['created_at'] = datetime.now().isoformat()
    
    print(f"\n[INFO] Added metadata:")
    print(f"   user_prompt: {original_user_prompt[:60]}...")
    print(f"   created_at: {workflow_json['workflow_metadata']['created_at']}")

    # Save Output
    output_path = Path(__file__).parent / "BA_op.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(workflow_json, f, indent=2)

    print(f"\n{'='*70}")
    print(f"[SUCCESS] Generated BA_op.json successfully")
    print(f"{'='*70}")
    print(f"   File: {output_path}")
    print(f"   Workflow ID: {workflow_json['workflow_metadata']['workflow_id']}")
    print(f"   Domain: {workflow_json['workflow_metadata']['domain']}")
    print(f"   Agents: {len(workflow_json['agents'])}")
    print(f"   User Prompt: {original_user_prompt}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    MODULE_NAME = "base_agent_4"
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