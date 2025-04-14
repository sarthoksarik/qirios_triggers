import time
from datetime import datetime
import os

def run_test():
    log_file = os.path.join(os.path.dirname(__file__), "script_log.txt")
    # log_file = '/tmp/script_log.txt'
    start_time = datetime.now()

    with open(log_file, "a") as f:
        f.write(f"\n--- Script started at: {start_time} ---\n")

    # Simulate a task
    time.sleep(5)

    end_time = datetime.now()
    with open(log_file, "a") as f:
        f.write(f"--- Script ended at: {end_time} ---\n")

    return {"status": "success", "start": str(start_time), "end": str(end_time)}