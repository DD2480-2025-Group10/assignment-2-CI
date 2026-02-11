import os
import shutil
import subprocess
from typing import Tuple

from src.models import BuildReport, BuildStatus


class BuildError(Exception):
    """Exception raised when a build step fails.

    Attributes:
        log_content: Complete log output from the failed build.
    """

    def __init__(self, message: str, log_content: str):
        super().__init__(message)
        self.log_content = log_content


def run_command(
    step_name: str, command: list[str], cwd: str, log: list[str]
) -> list[str]:
    """Execute a command and log its output.

    Args:
        step_name: Name of the build step.
        command: Command and arguments to execute.
        cwd: Working directory for the command.
        log: Existing log entries to append to.

    Returns:
        Updated log with this command's output.

    Raises:
        BuildError: If the command exits with non-zero status.
    """
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


def build_project(
    repo_url: str, branch: str, commit_id: str
) -> Tuple[BuildReport, str]:
    """Build and test a project from a Git repository.

    Clones the repository, checks out the specified commit, creates a virtual
    environment, installs dependencies, performs syntax checking, and runs tests.

    Args:
        repo_url: HTTPS URL of the Git repository.
        branch: Branch name to checkout.
        commit_id: Full commit SHA to build.

    Returns:
        BuildReport with build status (SUCCESS, FAILURE, or ERROR).
        str with all build logs
    """
    report = BuildReport(state=BuildStatus.PENDING)
    print(f"[LOG] Start processing commit {commit_id} on {branch}")

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
            ["python3.13", "-m", "venv", venv_dir],
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

        report = BuildReport(state=BuildStatus.SUCCESS, description="Build succeeded")

    except BuildError as e:
        report = BuildReport(state=BuildStatus.FAILURE, description="Build failed")
        print(f"Build error: {e}")

    except Exception as e:
        report = BuildReport(BuildStatus.ERROR, description="System error during build")
        print(f"System error: {str(e)}")
        log.append(f"\nSystem Error: {str(e)}")
    finally:
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)

    return report, "\n".join(log)
