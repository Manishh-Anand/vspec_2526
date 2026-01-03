import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

def load_metrics(log_file: str = 'timing_log.jsonl'):
    """Load metrics from JSONL file"""
    if not Path(log_file).exists():
        print(f"No log file found at {log_file}")
        return []
    
    metrics = []
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                metrics.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return metrics

def print_summary(metrics):
    """Print summary of metrics"""
    if not metrics:
        return

    df = pd.DataFrame(metrics)
    
    print("\n" + "="*60)
    print("PERFORMANCE METRICS SUMMARY")
    print("="*60)
    
    # Group by module
    summary = df.groupby('module')['duration_seconds'].agg(['count', 'mean', 'min', 'max', 'sum'])
    summary.columns = ['Runs', 'Avg (s)', 'Min (s)', 'Max (s)', 'Total (s)']
    
    print("\nModule Performance:")
    print(summary.round(2).to_string())
    
    print("\n" + "="*60)
    
    # Recent runs
    print("\nRecent Runs (Last 10):")
    recent = df.tail(10)[['timestamp', 'module', 'duration_seconds']]
    print(recent.to_string(index=False))

if __name__ == "__main__":
    try:
        import pandas as pd
    except ImportError:
        print("pandas not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])
        import pandas as pd

    metrics = load_metrics()
    print_summary(metrics)
