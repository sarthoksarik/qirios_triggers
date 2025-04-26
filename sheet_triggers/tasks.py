from celery import shared_task
from pathlib import Path
import subprocess
import platform

@shared_task
def run_external_script():
    system_name = platform.node()

    if "Sariks-MacBook" in system_name:
        # Local MacBook
        base_path = Path("/Users/sariksadman/works/qirios/sms_tracking")
    else:
        # VPS
        base_path = Path("/home/sarik/SMS_TRACKING")

    script_path = base_path / "call_log_track.py"
    python_path = base_path / "venv/bin/python3"

    try:
        result = subprocess.run(
            [str(python_path), str(script_path)],
            cwd=base_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": e.stderr}

@shared_task
def run_external_script_sms():
    system_name = platform.node()

    if "Sariks-MacBook" in system_name:
        # Local MacBook
        base_path = Path("/Users/sariksadman/works/qirios/sms_tracking")
    else:
        # VPS
        base_path = Path("/home/sarik/SMS_TRACKING")

    script_path = base_path / "sms_track.py"
    python_path = base_path / "venv/bin/python3"

    try:
        result = subprocess.run(
            [str(python_path), str(script_path)],
            cwd=base_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": e.stderr}
