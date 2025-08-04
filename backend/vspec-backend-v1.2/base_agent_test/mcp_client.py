import asyncio
import json
import requests
from typing import Dict, List, Any
from config import Config

class MCPSequentialThinkingClient:
    """Client to interact with Smithery AI Sequential Thinking Tools MCP Server"""
    
    def __init__(self):
        self.smithery_api_key = Config.SMITHERY_API_KEY
        self.deepseek_url = Config.DEEPSEEK_API_URL
        self.mcp_base_url = Config.SMITHERY_MCP_URL
        
    async def analyze_star_prompt(self, star_prompt: str) -> Dict[str, Any]:
        """Use Sequential Thinking MCP to analyze STAR prompt"""
        
        print("\n" + "="*60)
        print("STARTING SEQUENTIAL THINKING ANALYSIS")
        print("="*60)
        
        # Step 1: Initial problem understanding
        step1_result = await self._sequential_thinking_step(
            star_prompt=star_prompt,
            thought="Let me analyze this STAR prompt to understand what automation workflow is needed and break down the problem scope",
            thought_number=1,
            total_thoughts=4,
            next_thought_needed=True
        )
        
        # Step 2: Identify sub-agents using DeepSeek
        agents_analysis = await self._analyze_with_deepseek(
            prompt=f"""
            Based on this STAR prompt, identify the specific sub-agents needed. Return JSON only.
            
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
            
            Analyze the actual requirements - do NOT use generic agent names.
            """,
            context="sub-agents identification"
        )
        
        step2_result = await self._sequential_thinking_step(
            star_prompt=star_prompt,
            thought=f"Based on the analysis, I've identified these sub-agents: {agents_analysis}",
            thought_number=2,
            total_thoughts=4,
            next_thought_needed=True
        )
        
        # Step 3: Map tools to agents using DeepSeek
        tools_analysis = await self._analyze_with_deepseek(
            prompt=f"""
            For these identified agents, specify the exact tools needed. Return JSON only.
            
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
            
            Create specific tools based on actual requirements.
            """,
            context="tools mapping"
        )
        
        step3_result = await self._sequential_thinking_step(
            star_prompt=star_prompt,
            thought=f"I've mapped the tools to agents: {tools_analysis}",
            thought_number=3,
            total_thoughts=4,
            next_thought_needed=True
        )
        
        # Step 4: Final refinement and output
        step4_result = await self._sequential_thinking_step(
            star_prompt=star_prompt,
            thought="Let me finalize the analysis and ensure all agents and tools are properly integrated",
            thought_number=4,
            total_thoughts=4,
            next_thought_needed=False
        )
        
        # Generate final output
        return await self._generate_final_output(agents_analysis, tools_analysis)
    
    async def _sequential_thinking_step(self, star_prompt: str, thought: str, thought_number: int, 
                                      total_thoughts: int, next_thought_needed: bool, 
                                      is_revision: bool = False) -> Dict:
        """Make a call to Ollama for sequential thinking"""
        
        try:
            prompt = f"""
            You are performing step {thought_number} of {total_thoughts} in analyzing this STAR prompt:
            {star_prompt}
            
            Current thought: {thought}
            
            Please provide your analysis and next steps.
            """
            
            payload = {
                "model": Config.DEEPSEEK_MODEL_NAME,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.deepseek_url}/api/generate",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result["response"]
                print(f"Step {thought_number}: {thought}")
                return {"analysis": analysis}
            else:
                print(f"Ollama API error: {response.status_code}")
                return {"error": f"Ollama call failed: {response.status_code}"}
                
        except Exception as e:
            print(f"Error calling Ollama: {str(e)}")
            return {"error": f"Ollama call failed: {str(e)}"}
    
    async def _analyze_with_deepseek(self, prompt: str, context: str) -> str:
        """Call local DeepSeek R1 7B for analysis"""
        
        try:
            payload = {
                "model": Config.DEEPSEEK_MODEL_NAME,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.deepseek_url}/api/generate",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result["response"]
                print(f"DeepSeek Analysis ({context}): Generated")
                return analysis
            else:
                print(f"DeepSeek API error: {response.status_code}")
                return f"Error: DeepSeek call failed"
                
        except Exception as e:
            print(f"Error calling DeepSeek for {context}: {str(e)}")
            return f"Error: {str(e)}"
    
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
            print()
        
        print("TOOLS TO BE CREATED & HOW SUB AGENTS WOULD USE THEM:")
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
            print()
        
        return {
            "analysis_complete": True,
            "sub_agents": agents if agents else agents_analysis,
            "tools": tools if tools else tools_analysis,
            "summary": {
                "total_agents": len(agents) if agents else "See raw analysis",
                "total_tools": len(tools) if tools else "See raw analysis"
            }
        }
