import subprocess
import ast
import sys
import re

try:
    # 1. Read system_prompt from System_prompt.py
    with open("System_prompt.py", "r") as f:
        code = f.read()
        tree = ast.parse(code)
        system_prompt = None
        for node in tree.body:
            if isinstance(node, ast.Assign) and node.targets[0].id == "system_prompt":
                system_prompt = ast.literal_eval(node.value)

    if system_prompt is None:
        raise ValueError("system_prompt not found in System_prompt.py")

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

    # 3. Run model locally using Ollama CLI
    try:
        result = subprocess.run(
            ["ollama", "run", "deepseek-r1"],
            input=full_prompt,
            capture_output=True,
            text=True,
            check=True
        )
        
        star_output = result.stdout.strip()
        
        if not star_output:
            raise ValueError("No output received from Ollama")

        # Remove <think>...</think> block if present
        star_output_clean = re.sub(r'<think>[\s\S]*?</think>', '', star_output, flags=re.IGNORECASE).strip()

        # 4. Save result to star_m.py
        with open("star_m.py", "w") as f:
            f.write(f'star_output = """{star_output_clean}"""\n')

        print("\n✅ STAR output saved to star_m.py (without <think> block)")
        print("\nGenerated STAR format:")
        print(star_output_clean)

    except subprocess.CalledProcessError as e:
        print(f"Error running Ollama: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
