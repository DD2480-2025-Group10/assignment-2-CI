# REMOVE THIS ASAP: ADDED TO ALLOW BUILD FROM MAIN
# type: ignore
import subprocess
import os
import shutil
from history import write_history
from notify import notify


class BuildErr(Exception):
    def __init__(self, message, log_content):
        super().__init__(message)
        self.log_content = log_content


def run_command(step_name, command, cwd, log):
    result = subprocess.run(
        command, cwd=cwd, capture_output=True, text=True, shell=False
    )
    log.append(f"\n---{step_name}---\n{result.stdout + result.stderr}")
    if result.returncode != 0:
        raise BuildErr

    return log


def build_project(repo_url, branch, commit_id):
    print(f"Start processing commit {commit_id} on {branch}")

    work_dir = f"./temp_builds/{commit_id}"
    os.mkdir(work_dir)
    log = []
    success = False
    try:
        log = run_command("Git Clone", ["git", "clone", repo_url], work_dir, log)
        log = run_command(
            "Create venv", ["python3", "-m", "venv", "venv"], work_dir, log
        )
        log = run_command(
            "Activate venv", ["source", "venv/bin/activate"], work_dir, log
        )
        log = run_command(
            "Install requirments",
            ["pip", "install", "-e", '".[dev]"'],
            work_dir,
            log,
        )
        log = run_command(
            "Git Checkout Branch", ["git", "checkout", branch], work_dir, log
        )
        log = run_command("Git Checkout", ["git", "checkout", commit_id], work_dir, log)
        log = run_command("Sytex Checking", ["mypy", "--strict", "."], work_dir, log)
        log = run_command("Unit Tests", ["pytest"], work_dir, log)

        success = True

    except BuildErr as e:
        success = False
        print(f"Build error at step {e}")

    except Exception as e:
        success = False
        print(f"System error: {str(e)}")
        log.append(f"\nSystem Error: {str(e)}")

    finally:
        final_log = "\n".join(log)
        write_history(success, commit_id, final_log)
        if success:
            notify(commit_id, "success")
        else:
            notify(commit_id, "failure")

        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)

    return success
