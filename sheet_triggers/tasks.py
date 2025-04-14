import subprocess
import platform
from celery import shared_task

@shared_task
def run_external_script():
    system_name = platform.node()

    if "Sariks-MacBook" in system_name:
        # Local MacBook
        script_path = "/Users/sariksadman/works/qirios/sms_tracking/call_log_track.py"
        python_path = "/Users/sariksadman/works/qirios/sms_tracking/venv/bin/python3"
        envd = "/Users/sariksadman/works/qirios/sms_tracking"  # sets working directory

    else:
        # VPS
        script_path = "/home/ubuntu/scripts/call_log_track.py"
        python_path = "/home/ubuntu/scripts/venv/bin/python3"
        envd = "/Users/sariksadman/works/qirios/sms_tracking"

    try:
        result = subprocess.run(
            [python_path, script_path],
            cwd=envd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": e.stderr}
