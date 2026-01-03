
import subprocess
import os

def list_tools():
    prompt = "List all enabled MCP tools you have access to. just list the names."
    cmd = ["powershell.exe", "-NoLogo", "-NoProfile", "-Command", "claude"]
    
    print(f"Querying Claude...")
    
    # We need to pipe input to claude
    process = subprocess.Popen(
        cmd, 
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True,
        cwd=r"C:\Users\manis"  # Using the home dir as CWD for Claude config access
    )
    
    stdout, stderr = process.communicate(input=prompt)
    
    print("--- STDOUT ---")
    print(stdout)
    print("--- STDERR ---")
    print(stderr)
    
    with open("my_tools.txt", "w", encoding="utf-8") as f:
        f.write(stdout)

if __name__ == "__main__":
    list_tools()
