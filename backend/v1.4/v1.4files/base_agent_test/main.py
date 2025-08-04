import asyncio
from mcp_client import MCPSequentialThinkingClient
from config import Config

async def main():
    """Main runner using Sequential Thinking MCP Server"""
    
    # Read STAR prompt from star_m.py
    try:
        with open(Config.STAR_PROMPT_FILE, "r") as f:
            star_content = f.read()
        
        # Extract the actual prompt content (you might need to parse this differently)
        # Assuming star_m.py contains the prompt as a string variable
        star_prompt = star_content
        
        print(f"Loaded STAR prompt from: {Config.STAR_PROMPT_FILE}")
        print(f"Prompt length: {len(star_prompt)} characters")
        
    except FileNotFoundError:
        print(f"Error: Could not find {Config.STAR_PROMPT_FILE}")
        star_prompt = input("Please enter your STAR prompt manually: ")
    
    # Initialize MCP client
    client = MCPSequentialThinkingClient()
    
    # Run the analysis
    result = await client.analyze_star_prompt(star_prompt)
    
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)
    print(f"Analysis Status: {'✓ Complete' if result.get('analysis_complete') else '✗ Failed'}")
    if result.get('summary'):
        print(f"Total Agents: {result['summary']['total_agents']}")
        print(f"Total Tools: {result['summary']['total_tools']}")

if __name__ == "__main__":
    asyncio.run(main())