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
        
    async def analyze_with_sequential_thinking(self, prompt: str, context: str) -> Dict[str, Any]:
        """Use Sequential Thinking to analyze a prompt"""
        
        print(f"\nAnalyzing {context} with Sequential Thinking...")
        
        # Step 1: Initial problem understanding
        step1_result = await self._sequential_thinking_step(
            prompt=prompt,
            thought=f"Let me analyze this {context} to understand the requirements and scope",
            thought_number=1,
            total_thoughts=4,
            next_thought_needed=True
        )
        
        # Step 2: Identify key components
        components_analysis = await self._analyze_with_deepseek(
            prompt=f"""
            Based on this {context}, identify the key components needed. Return JSON only.
            
            Context: {prompt}
            
            Return JSON array with specific components based on the context.
            """,
            context=f"{context} components"
        )
        
        step2_result = await self._sequential_thinking_step(
            prompt=prompt,
            thought=f"Based on the analysis, I've identified these components: {components_analysis}",
            thought_number=2,
            total_thoughts=4,
            next_thought_needed=True
        )
        
        # Step 3: Map relationships
        relationships_analysis = await self._analyze_with_deepseek(
            prompt=f"""
            For these identified components, specify their relationships and dependencies. Return JSON only.
            
            Context: {prompt}
            Components: {components_analysis}
            
            Return JSON object showing relationships between components.
            """,
            context=f"{context} relationships"
        )
        
        step3_result = await self._sequential_thinking_step(
            prompt=prompt,
            thought=f"I've mapped the relationships: {relationships_analysis}",
            thought_number=3,
            total_thoughts=4,
            next_thought_needed=True
        )
        
        # Step 4: Final refinement
        step4_result = await self._sequential_thinking_step(
            prompt=prompt,
            thought="Let me finalize the analysis and ensure all components are properly integrated",
            thought_number=4,
            total_thoughts=4,
            next_thought_needed=False
        )
        
        # Generate final output
        return await self._generate_final_output(components_analysis, relationships_analysis)
    
    async def _sequential_thinking_step(self, prompt: str, thought: str, thought_number: int, 
                                      total_thoughts: int, next_thought_needed: bool) -> Dict:
        """Make a call to DeepSeek for sequential thinking"""
        
        try:
            step_prompt = f"""
            You are performing step {thought_number} of {total_thoughts} in analyzing this:
            {prompt}
            
            Current thought: {thought}
            
            Please provide your analysis and next steps.
            """
            
            payload = {
                "model": Config.DEEPSEEK_MODEL_NAME,
                "prompt": step_prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.deepseek_url}/v1/completions",
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
                print(f"DeepSeek API error: {response.status_code}")
                return {"error": f"DeepSeek call failed: {response.status_code}"}
                
        except Exception as e:
            print(f"Error calling DeepSeek: {str(e)}")
            return {"error": f"DeepSeek call failed: {str(e)}"}
    
    async def _analyze_with_deepseek(self, prompt: str, context: str) -> str:
        """Call DeepSeek for analysis"""
        
        try:
            payload = {
                "model": Config.DEEPSEEK_MODEL_NAME,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.deepseek_url}/v1/completions",
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
    
    async def _generate_final_output(self, components_analysis: str, relationships_analysis: str) -> Dict[str, Any]:
        """Generate and return the final analysis output"""
        
        try:
            # Parse the DeepSeek responses
            components = json.loads(components_analysis) if components_analysis.startswith('[') else []
            relationships = json.loads(relationships_analysis) if relationships_analysis.startswith('{') else {}
            
            return {
                "status": "success",
                "components": components,
                "relationships": relationships,
                "message": "Analysis completed successfully"
            }
            
        except json.JSONDecodeError:
            print("Error parsing DeepSeek responses")
            return {
                "status": "error",
                "message": "Error parsing analysis results",
                "components": [],
                "relationships": {}
            } 