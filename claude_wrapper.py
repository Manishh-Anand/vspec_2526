#!/usr/bin/env python3
"""
claude_wrapper.py

Reads a prompt from `example_input`, sends it to the `claude` CLI while running
in TARGET_CWD ("C:\\Users\\manis"), captures the result and writes it to `example_op`.

It temporarily changes the current working directory so that the `claude` CLI
will find the local .claude.json and MCP servers installed under that user folder.
"""

import os
import subprocess
import shutil
import sys
import time
from pathlib import Path
from contextlib import contextmanager

# Optional: interactive fallback using pexpect
try:
    import pexpect
    from pexpect import popen_spawn
except Exception:
    pexpect = None
    popen_spawn = None

# Config
INPUT_FILE = Path("example_input")
OUTPUT_FILE = Path("example_op")
CLAUDE_CMD = "claude"   # command to run; adjust to full path if needed
TIMEOUT_SECONDS = 60
DEBUG = False

# IMPORTANT: target working directory where .claude.json and MCP servers live
TARGET_CWD = Path(r"C:\Users\manis")

@contextmanager
def pushd(new_dir: Path):
    """Temporarily chdir to `new_dir`, then restore the original cwd."""
    orig = Path.cwd()
    try:
        os.chdir(str(new_dir))
        if DEBUG:
            print(f"[debug] changed cwd: {orig} -> {new_dir}")
        yield
    finally:
        os.chdir(str(orig))
        if DEBUG:
            print(f"[debug] restored cwd: {new_dir} -> {orig}")

def read_prompt():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"{INPUT_FILE} not found (looked in {Path.cwd()})")
    return INPUT_FILE.read_text(encoding="utf-8")

def write_output(text: str):
    OUTPUT_FILE.write_text(text, encoding="utf-8")
    if DEBUG:
        print(f"[debug] wrote {len(text)} bytes to {OUTPUT_FILE} (in {Path.cwd()})")

def run_noninteractive(prompt: str):
    """
    Try to run claude non-interactively by piping prompt to stdin.
    Run inside TARGET_CWD so the CLI picks up local config.
    """
    if DEBUG:
        print("[debug] Attempting subprocess.run (non-interactive) ...")
    try:
        # Use pushd to ensure cwd for the subprocess
        with pushd(TARGET_CWD):
            proc = subprocess.run(
                [CLAUDE_CMD],
                input=prompt,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=TIMEOUT_SECONDS,
            )
    except FileNotFoundError:
        raise FileNotFoundError(f"Command `{CLAUDE_CMD}` not found in PATH when run from {TARGET_CWD}.")
    except subprocess.TimeoutExpired as e:
        raise TimeoutError(f"Subprocess timeout after {TIMEOUT_SECONDS}s")

    if DEBUG:
        print(f"[debug] returncode={proc.returncode}")
        print(f"[debug] stdout (first 200 chars): {proc.stdout[:200]!r}")
        print(f"[debug] stderr (first 200 chars): {proc.stderr[:200]!r}")

    if proc.stdout and proc.stdout.strip():
        return proc.stdout
    return proc.stderr

def run_interactive_with_pexpect(prompt: str):
    """
    Interactive driver using pexpect.popen_spawn.PopenSpawn while inside TARGET_CWD.
    You may need to tune read loops or add explicit expect patterns for reliability.
    """
    if pexpect is None or popen_spawn is None:
        raise RuntimeError("pexpect not installed. Install with: pip install pexpect")

    if DEBUG:
        print("[debug] Attempting pexpect interactive session ...")

    with pushd(TARGET_CWD):
        child = popen_spawn.PopenSpawn(CLAUDE_CMD, timeout=TIMEOUT_SECONDS, encoding="utf-8")
        out = []
        try:
            # small sleep to allow banner/prompt
            time.sleep(0.2)
            try:
                initial = child.read_nonblocking(size=4096, timeout=0.1)
                out.append(initial)
            except Exception:
                pass

            # send the prompt; append newline to simulate Enter
            child.sendline(prompt)

            # read until EOF or process exit (tune as needed)
            while True:
                try:
                    chunk = child.read_nonblocking(size=4096, timeout=1)
                    if chunk:
                        out.append(chunk)
                    else:
                        if child.isalive():
                            continue
                        else:
                            break
                except pexpect.TIMEOUT:
                    if not child.isalive():
                        break
                    # continue waiting until overall timeout
                except pexpect.EOF:
                    break
        finally:
            try:
                child.close(force=True)
            except Exception:
                pass

    return "".join(out)

def main():
    # Validate TARGET_CWD
    if not TARGET_CWD.exists() or not TARGET_CWD.is_dir():
        print(f"Error: TARGET_CWD {TARGET_CWD} does not exist or is not a directory.", file=sys.stderr)
        sys.exit(2)

    # Ensure claude is available in PATH or is runnable from TARGET_CWD
    # We do NOT require it to be in PATH if it is an executable in TARGET_CWD,
    # because running inside TARGET_CWD may allow relative invocation.
    if not shutil.which(CLAUDE_CMD):
        if (TARGET_CWD / CLAUDE_CMD).exists() or (TARGET_CWD / (CLAUDE_CMD + ".exe")).exists():
            if DEBUG:
                print(f"[debug] `{CLAUDE_CMD}` not in PATH, but found in {TARGET_CWD}. Will run from there.")
        else:
            print(f"Warning: `{CLAUDE_CMD}` not found in PATH and not found in {TARGET_CWD}.", file=sys.stderr)
            # we still attempt to run because user might have an environment where the command resolves only when in TARGET_CWD
    try:
        # read prompt from the wrapper's current directory (this is usually where you run the wrapper)
        prompt = read_prompt()
    except FileNotFoundError:
        # If example_input not found in current dir, also try reading it from TARGET_CWD
        if (TARGET_CWD / INPUT_FILE).exists():
            if DEBUG:
                print(f"[debug] {INPUT_FILE} not in {Path.cwd()}, reading from {TARGET_CWD} instead.")
            with pushd(TARGET_CWD):
                prompt = read_prompt()
        else:
            raise

    # Try non-interactive first (simpler)
    try:
        output = run_noninteractive(prompt)
        if not output or not output.strip():
            if DEBUG:
                print("[debug] No output from non-interactive run; trying interactive fallback.")
            raise RuntimeError("empty output from non-interactive run")
    except Exception as e:
        if DEBUG:
            print(f"[debug] Non-interactive attempt failed: {e}")
        # fallback to interactive using pexpect
        try:
            output = run_interactive_with_pexpect(prompt)
        except Exception as e2:
            print(f"Error: both non-interactive and interactive attempts failed.\n"
                  f"Non-interactive error: {e}\nInteractive error: {e2}",
                  file=sys.stderr)
            sys.exit(3)

    # write the result to OUTPUT_FILE in the current working directory where the wrapper was launched.
    write_output(output)
    print(f"Done — output written to {OUTPUT_FILE} (cwd: {Path.cwd()})")

if __name__ == "__main__":
    main()
