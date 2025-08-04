class Config:
    # Smithery AI MCP Server configuration
    SMITHERY_API_KEY = "78bac862-150f-4f0c-9613-83728af041c5"  # Replace with your actual API key
    SMITHERY_MCP_URL = "https://smithery.ai/server/@xinzhongyouhai/mcp-sequentialthinking-tools"     # Smithery MCP base URL
    
    # DeepSeek R1 7B configuration
    # Adjust based on your local setup:
    
    # For Ollama setup:
    DEEPSEEK_API_URL = "http://localhost:11434"
    DEEPSEEK_MODEL_NAME = "deepseek-r1:7b"
    
    # For direct API setup:
    # DEEPSEEK_API_URL = "http://localhost:8000"
    
    # For OpenAI-compatible API:
    # DEEPSEEK_API_URL = "http://localhost:1234"
    
    # File paths
    STAR_PROMPT_FILE = "/Users/jspranav/Downloads/final_yr_project_2526/backend/vspec-backend-v1.2/star_m.py"
    OUTPUT_DIR = "./outputs/"