import os
import shutil
import subprocess

from src.models import BuildReport, BuildStatus


class BuildError(Exception):
    def __init__(self, message: str, log_content: str):
        super().__init__(message)
        self.log_content = log_content


def run_command(
    step_name: str, command: list[str], cwd: str, log: list[str]
) -> list[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        shell=False,
    )
    log.append(f"\n---{step_name}---\n{result.stdout}{result.stderr}")
    if result.returncode != 0:
        raise BuildError(
            f"{step_name} failed (exit={result.returncode})", "\n".join(log)
        )

    return log


def build_project(repo_url: str, branch: str, commit_id: str) -> BuildReport:
    status = BuildStatus.PENDING
    print(f"Start processing commit {commit_id} on {branch}")

    base_dir = os.path.abspath("./temp_builds")
    work_dir = os.path.join(base_dir, commit_id)
    os.makedirs(work_dir, exist_ok=True)

    repo_dir = os.path.join(work_dir, "repo")
    venv_dir = os.path.join(work_dir, "venv")
    venv_python = os.path.join(venv_dir, "bin", "python")
    venv_pip = os.path.join(venv_dir, "bin", "pip")
    venv_pytest = os.path.join(venv_dir, "bin", "pytest")

    log: list[str] = []

    try:
        log = run_command(
            "Git Clone",
            ["git", "clone", repo_url, repo_dir],
            cwd=work_dir,
            log=log,
        )

        log = run_command(
            "Git Checkout Branch",
            ["git", "checkout", branch],
            cwd=repo_dir,
            log=log,
        )
        log = run_command(
            "Git Checkout Commit",
            ["git", "checkout", commit_id],
            cwd=repo_dir,
            log=log,
        )

        log = run_command(
            "Create venv",
            ["python3", "-m", "venv", venv_dir],
            cwd=work_dir,
            log=log,
        )
        log = run_command(
            "Upgrade pip",
            [venv_python, "-m", "pip", "install", "--upgrade", "pip"],
            cwd=work_dir,
            log=log,
        )

        log = run_command(
            "Install requirements",
            [venv_pip, "install", "-e", ".[dev]"],
            cwd=repo_dir,
            log=log,
        )

        log = run_command(
            "Syntax Checking",
            [venv_python, "-m", "compileall", "-q", "."],
            cwd=repo_dir,
            log=log,
        )

        log = run_command(
            "Unit Tests",
            [venv_pytest],
            cwd=repo_dir,
            log=log,
        )

        status = BuildStatus.SUCCESS

    except BuildError as e:
        status = BuildStatus.FAILURE
        print(f"Build error: {e}")

    except Exception as e:
        status = BuildStatus.ERROR
        print(f"System error: {str(e)}")
        log.append(f"\nSystem Error: {str(e)}")

    finally:
        final_log = "\n".join(log)
        res = BuildReport(state=status)

        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)

    return res
