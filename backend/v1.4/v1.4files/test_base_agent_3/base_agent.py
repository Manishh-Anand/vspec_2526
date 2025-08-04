import sys
import requests
import importlib.util
from pathlib import Path


class BaseAgent:
    def __init__(self, input_file, output_file, api_url="http://localhost:11434/api/generate"):
        self.input_file = input_file
        self.output_file = output_file
        self.api_url = api_url
        self.prompt_content = None

        self.system_prompt = """You are a Base Agent in an agentic system. Your role is to:

1. Read and understand the user prompt/task
2. Maintain context throughout workflow analysis
3. Analyze tasks and determine which MCP tools need to be called
4. Manage workflow execution and coordinate tool usage
5. Handle error recovery and fallback strategies
6. Based on the user prompt, list out the sub-agents sequentially to fulfill the task
7. List the tools that need to be created
8. Explain how the sub-agents will use the tools to complete the work




Analyze the given task and provide:
- Sub-agents needed (in sequence)
- Tools required
- How sub-agents will use tools
- Workflow execution plan
- Error handling approach
- 



Stick to region‑friendly tools (skip anything with Chinese‑language interfaces) and spell out the auth/permission steps whenever you talk about hooking apps together.

Be specific and actionable in your response."""

    def read_prompt_from_py_file(self):

        """Dynamically load Python file and extract 'star_output'"""

        try:
            spec = importlib.util.spec_from_file_location("prompt_module", self.input_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, 'star_output'):
                self.prompt_content = module.star_output
                print(f"Loaded 'star_output' from {self.input_file}")
                return True
            else:
                print(f"'star_output' not found in {self.input_file}")
                return False
        except Exception as e:
            print(f"Error loading prompt file: {e}")
            return False

    def call_local_llm(self, user_prompt):

        """Send prompt to local Ollama LLM (DeepSeek R1 7B)"""

        try:
            full_prompt = f"{self.system_prompt}\n\nUSER TASK:\n{user_prompt}\n\nANALYSIS:"
            payload = {
                "model": "deepseek-r1:7b",
                "prompt": full_prompt,
                "stream": False
            }

            print("Sending prompt to Ollama...")
            response = requests.post(self.api_url, json=payload)

            if response.status_code == 200:
                result = response.json()
                llm_response = result.get("response", "")
                print("LLM response received")
                return llm_response
            else:
                print(f"LLM API error {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Failed to call LLM: {e}")
            return None

    def write_output(self, llm_response):
        """Save LLM output to the specified file"""
        try:
            output_path = Path(self.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("BASE AGENT ANALYSIS\n")
                f.write("=" * 50 + "\n\n")
                f.write("ORIGINAL TASK:\n")
                f.write("-" * 20 + "\n")
                f.write(self.prompt_content + "\n\n")
                f.write("LLM ANALYSIS:\n")
                f.write("-" * 20 + "\n")
                f.write(llm_response + "\n")

            print(f"Output saved to {self.output_file}")
            return True
        except Exception as e:
            print(f"Failed to write output: {e}")
            return False

    def run(self):
        """Run the whole Base Agent pipeline"""
        print("Base Agent Starting")

        if not self.read_prompt_from_py_file():
            return

        llm_response = self.call_local_llm(self.prompt_content)
        if not llm_response:
            return

        if not self.write_output(llm_response):
            return

        print("Base Agent completed successfully!")


def main():
   
    input_file = "/Users/jspranav/Downloads/final_yr_project_2526/backend/v1.4/v1.4files/star_m.py"
    output_file = "/Users/jspranav/Downloads/final_yr_project_2526/backend/v1.4/v1.4files/test_base_agent_3/base_ag_output.txt"
    api_url = "http://localhost:11434/api/generate"  # Ollama: swap api key / url

    agent = BaseAgent(input_file, output_file, api_url)
    agent.run()


if __name__ == "__main__":
    main()
