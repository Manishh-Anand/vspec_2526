import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "deepseek/deepseek-chat-v3-0324:free",
    "messages": [
        {"role": "user", "content": "So you are a baseagent who delgates tasks to subagents to perforn the tasks the user gives you via prompt. the promt is(im a iran citizen and want to have a 3 day holiday in india delhi,so suggest me a deltailed plan including hotel,flight,visa,travel,food etc and also solve any conflicts with flight and hotel booking so that the tourist does'nt get staranded)."}
    ]
}

response = requests.post(url, headers=headers, json=payload)

try:
    data = response.json()
    if "choices" in data:
        print("AI Response:\n", data["choices"][0]["message"]["content"])
    else:
        print("Error:", data.get("error", "Unknown error"))
except Exception as e:
    print("Failed to parse response:", e)
