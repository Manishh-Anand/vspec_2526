# import subprocess
# import ast
# import sys
# import re

# try:
#     # 1. Read system_prompt from System_prompt.py
#     with open("System_prompt.py", "r") as f:
#         code = f.read()
#         tree = ast.parse(code)
#         system_prompt = None
#         for node in tree.body:
#             if isinstance(node, ast.Assign) and node.targets[0].id == "system_prompt":
#                 system_prompt = ast.literal_eval(node.value)

#     if system_prompt is None:
#         raise ValueError("system_prompt not found in System_prompt.py")

#     # 2. Create the full prompt for STAR method
#     full_prompt = f"""
# Convert the following into a detailed STAR method format.

# Prompt: "{system_prompt}"

# Format:
# S (Situation): ...
# T (Task): ...
# A (Action): ...
# R (Result): ...
# """

#     # 3. Run model locally using Ollama CLI
#     try:
#         result = subprocess.run(
#             ["ollama", "run", "deepseek-r1"],
#             input=full_prompt,
#             capture_output=True,
#             text=True,
#             check=True
#         )
        
#         star_output = result.stdout.strip()
        
#         if not star_output:
#             raise ValueError("No output received from Ollama")

#         # Remove <think>...</think> block if present
#         star_output_clean = re.sub(r'<think>[\s\S]*?</think>', '', star_output, flags=re.IGNORECASE).strip()

#         # 4. Save result to star_m.py
#         with open("star_m.py", "w") as f:
#             f.write(f'star_output = """{star_output_clean}"""\n')

#         print("\nSTAR output saved to star_m.py (without <think> block)")
#         print("\nGenerated STAR format:")
#         print(star_output_clean)

#     except subprocess.CalledProcessError as e:
#         print(f"Error running Ollama: {e}")
#         print(f"Error output: {e.stderr}")
#         sys.exit(1)

# except Exception as e:
#     print(f"An error occurred: {e}")
#     sys.exit(1)

import subprocess
import ast
import sys
import re
import json
from pathlib import Path

try:
    # 1. Read system_prompt from System_prompt.py
    current_dir = Path(__file__).parent
    prompt_file = current_dir / "System_prompt.py"
    
    with open(prompt_file, "r") as f:
        code = f.read()
        tree = ast.parse(code)
        system_prompt = None
        for node in tree.body:
            if isinstance(node, ast.Assign) and node.targets[0].id == "system_prompt":
                system_prompt = ast.literal_eval(node.value)

    if system_prompt is None:
        raise ValueError(f"system_prompt not found in {prompt_file}")

    # 2. Create the full prompt for STAR method
    full_prompt = f"""
Convert the following into a detailed STAR method format.

Prompt: "{system_prompt}"

Format:
S (Situation): ...
T (Task): ...
A (Action): ...
R (Result): ...
"""

    # 3. Run model locally using LM Studio API
    try:
        # Prepare JSON payload for LM Studio API
        payload = {
            "model": "qwen2.5-coder-14b-instruct",
            "messages": [{"role": "user", "content": full_prompt}],
            "temperature": 0.7,
            "max_tokens": 5000
        }
        
        # Use curl to call LM Studio API
        print(f"Calling LM Studio model: {payload['model']}...")
        result = subprocess.run([
            "curl", "-X", "POST",
            "http://localhost:1234/v1/chat/completions",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload)
        ], capture_output=True, text=True, check=True)
        
        response_json = json.loads(result.stdout)
        star_output = response_json["choices"][0]["message"]["content"].strip()
        
        if not star_output:
            raise ValueError("No output received from LM Studio")

        # Remove <think>...</think> block if present
        star_output_clean = re.sub(r'<think>[\s\S]*?</think>', '', star_output, flags=re.IGNORECASE).strip()
        star_output_clean = re.sub(r'```.*?```', '', star_output_clean, flags=re.DOTALL).strip() # Remove code blocks if any
        star_output_clean = star_output_clean.strip('`').strip()

        # 4. Save result to star_m.py
        output_file = current_dir / "star_m.py"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f'star_output = """{star_output_clean}"""\n')

        print(f"\nSTAR output saved to {output_file}")
        print("\nGenerated STAR format (preview):")
        print(star_output_clean[:200] + "...")

    except subprocess.CalledProcessError as e:
        print(f"Error connecting to LM Studio: {e}")
        print(f"Error output: {e.stderr}")
        print("Make sure LM Studio is running and the server is started on localhost:1234")
        sys.exit(1)

except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)


























