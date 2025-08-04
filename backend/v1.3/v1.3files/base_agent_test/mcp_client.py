import asyncio
import json
import requests
import time
import re
from typing import Dict, List, Any
from config import Config

def extract_json_array(text):
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        return match.group(0)
    return text  # fallback to raw text if no JSON found

class MCPSequentialThinkingClient:
    """Client to interact with local Ollama for analysis"""
    
    def __init__(self):
        self.deepseek_url = Config.DEEPSEEK_API_URL
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        
    async def analyze_star_prompt(self, star_prompt: str) -> Dict[str, Any]:
        """Analyze STAR prompt using local Ollama"""
        
        print("\n" + "="*60)
        print("STARTING ANALYSIS")
        print("="*60)
        
        # Step 1: Identify sub-agents using DeepSeek
        agents_analysis = await self._analyze_with_deepseek(
            prompt=f"""
            Based on this STAR prompt, identify the specific sub-agents needed.
            Return ONLY a JSON array, with no explanation, markdown, or extra text.
            Do not include any text before or after the JSON array.

            STAR Prompt: {star_prompt}

            Return JSON array:
            [
                {{
                    "name": "SpecificAgentName",
                    "responsibility": "what this agent does",
                    "capabilities": ["specific", "capabilities"],
                    "integration": ["how it connects with other agents"]
                }}
            ]
            """,
            context="sub-agents identification"
        )
        
        # Step 2: Map tools to agents using DeepSeek
        tools_analysis = await self._analyze_with_deepseek(
            prompt=f"""
            For these identified agents, specify the exact tools needed.
            Return ONLY a JSON array, with no explanation, markdown, or extra text.
            Do not include any text before or after the JSON array.

            STAR Prompt: {star_prompt}
            Identified Agents: {agents_analysis}

            Return JSON array:
            [
                {{
                    "name": "SpecificToolName",
                    "purpose": "what this tool does",
                    "used_by": "which agent uses it",
                    "integration": "how it connects with other tools/agents"
                }}
            ]
            """,
            context="tools mapping"
        )
        
        # Generate final output
        return await self._generate_final_output(agents_analysis, tools_analysis)
    
    async def _analyze_with_deepseek(self, prompt: str, context: str) -> str:
        """Call local DeepSeek R1 for analysis with retry logic"""
        
        for attempt in range(self.max_retries):
            try:
                payload = {
                    "model": Config.DEEPSEEK_MODEL_NAME,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 2048,  # Increased for longer responses
                        "stop": ["</think>", "```"]  # Stop tokens to prevent incomplete responses
                    }
                }
                
                print(f"\nSending request to Ollama for {context} (Attempt {attempt + 1}/{self.max_retries})...")
                response = requests.post(
                    f"{self.deepseek_url}/api/generate",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=180  # Increased timeout to 180 seconds
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "response" in result:
                        analysis = result["response"]
                        # Clean up the response
                        analysis = analysis.replace("<think>", "").replace("</think>", "").strip()
                        # Extract JSON array if present
                        analysis = extract_json_array(analysis)
                        print(f"DeepSeek Analysis ({context}): Generated successfully")
                        return analysis
                    else:
                        print(f"Unexpected response format: {result}")
                        if attempt < self.max_retries - 1:
                            print(f"Retrying in {self.retry_delay} seconds...")
                            await asyncio.sleep(self.retry_delay)
                            continue
                        return f"Error: Unexpected response format"
                else:
                    print(f"DeepSeek API error: {response.status_code}")
                    print(f"Response: {response.text}")
                    if attempt < self.max_retries - 1:
                        print(f"Retrying in {self.retry_delay} seconds...")
                        await asyncio.sleep(self.retry_delay)
                        continue
                    return f"Error: DeepSeek call failed with status {response.status_code}"
                    
            except requests.exceptions.Timeout:
                print(f"Timeout while calling DeepSeek for {context}. The model might need more time to generate a response.")
                if attempt < self.max_retries - 1:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
                    continue
                return f"Error: Request timed out after 180 seconds"
            except requests.exceptions.ConnectionError:
                print(f"Connection error while calling DeepSeek for {context}. Please check if Ollama is running.")
                if attempt < self.max_retries - 1:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
                    continue
                return f"Error: Could not connect to Ollama server"
            except Exception as e:
                print(f"Error calling DeepSeek for {context}: {str(e)}")
                if attempt < self.max_retries - 1:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
                    continue
                return f"Error: {str(e)}"
        
        return f"Error: All {self.max_retries} attempts failed"
    
    async def _generate_final_output(self, agents_analysis: str, tools_analysis: str) -> Dict[str, Any]:
        """Generate and print the final analysis output"""
        
        try:
            # Parse the DeepSeek responses
            agents = json.loads(agents_analysis) if agents_analysis.startswith('[') else []
            tools = json.loads(tools_analysis) if tools_analysis.startswith('[') else []
        except json.JSONDecodeError:
            print("Error parsing DeepSeek responses, using raw text")
            agents = []
            tools = []
        
        print("\n" + "="*60)
        print("BASE AGENT ANALYSIS COMPLETE")
        print("="*60)
        
        print("\nSUB AGENTS REQUIRED TO BUILD:")
        print("-" * 30)
        if agents:
            for i, agent in enumerate(agents, 1):
                print(f"{i}. {agent.get('name', 'Unknown Agent')}")
                print(f"   Responsibility: {agent.get('responsibility', 'Not specified')}")
                print(f"   Capabilities: {', '.join(agent.get('capabilities', []))}")
                print(f"   Integration: {', '.join(agent.get('integration', []))}")
                print()
        else:
            print("Raw agents analysis:")
            print(agents_analysis)
        
        print("\nTOOLS TO BE CREATED & HOW SUB AGENTS WOULD USE THEM:")
        print("-" * 50)
        if tools:
            for i, tool in enumerate(tools, 1):
                print(f"{i}. {tool.get('name', 'Unknown Tool')}")
                print(f"   Purpose: {tool.get('purpose', 'Not specified')}")
                print(f"   Used by: {tool.get('used_by', 'Not specified')}")
                print(f"   Integration: {tool.get('integration', 'Not specified')}")
                print()
        else:
            print("Raw tools analysis:")
            print(tools_analysis)
        
        print("\n" + "="*60)
        print("ANALYSIS SUMMARY")
        print("="*60)
        print(f"Analysis Status: {'✓ Complete' if agents and tools else '⚠ Partial'}")
        print(f"Total Agents: {len(agents) if agents else 'See raw analysis'}")
        print(f"Total Tools: {len(tools) if tools else 'See raw analysis'}")
        
        return {
            "agents": agents,
            "tools": tools,
            "status": "complete" if agents and tools else "partial"
        }
