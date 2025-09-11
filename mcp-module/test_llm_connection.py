import httpx
import asyncio
import json

async def test_llm():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "model": "openhermes-2.5-mistral-7b",
                "messages": [
                    {"role": "user", "content": "Hello"}
                ],
                "max_tokens": 10
            }
            
            print("Testing LLM connection...")
            response = await client.post('http://127.0.0.1:1234/v1/chat/completions', json=payload)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Success! Response: {result}")
            else:
                print(f"Error: {response.text}")
                
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm())
