import src.builder as builder
from src.models import BuildStatus


class FakeRunCommand:
    def __init__(self, fail_step: str | None = None, raise_generic: bool = False):
        self.fail_step = fail_step
        self.raise_generic = raise_generic
        self.steps: list[str] = []

    def __call__(self, step_name: str, command: list[str], cwd: str, log: list[str]):
        self.steps.append(step_name)

        if self.raise_generic:
            # Simulate an unexpected error inside a build step
            raise RuntimeError("boom")

        if self.fail_step is not None and step_name == self.fail_step:
            # Simulate a build step failure
            raise builder.BuildError(f"{step_name} failed", "\n".join(log))

        log.append(f"{step_name} OK")
        return log


def test_build_project_success(monkeypatch):
    fake = FakeRunCommand()
    monkeypatch.setattr(builder, "run_command", fake)

    report = builder.build_project(
        repo_url="https://example.com/owner/repo.git",
        branch="refs/heads/main",
        commit_id="abc123",
    )

    assert report.state == BuildStatus.SUCCESS
    assert "Git Clone" in fake.steps
    assert "Syntax Checking" in fake.steps
    assert "Unit Tests" in fake.steps


def test_build_project_fails_on_syntax_error(monkeypatch):
    fake = FakeRunCommand(fail_step="Syntax Checking")
    monkeypatch.setattr(builder, "run_command", fake)

    report = builder.build_project(
        repo_url="https://example.com/owner/bad-repo.git",
        branch="refs/heads/main",
        commit_id="deadbeef",
    )

    assert report.state == BuildStatus.FAILURE
    # Syntax step was reached, but tests never ran
    assert "Syntax Checking" in fake.steps
    assert "Unit Tests" not in fake.steps


def test_build_project_fails_on_test_failure(monkeypatch):
    fake = FakeRunCommand(fail_step="Unit Tests")
    monkeypatch.setattr(builder, "run_command", fake)

    report = builder.build_project(
        repo_url="https://example.com/owner/failing-tests.git",
        branch="refs/heads/main",
        commit_id="cafebabe",
    )

    assert report.state == BuildStatus.FAILURE
    assert "Unit Tests" in fake.steps


def test_build_project_reports_system_error(monkeypatch):
    fake = FakeRunCommand(raise_generic=True)
    monkeypatch.setattr(builder, "run_command", fake)

    report = builder.build_project(
        repo_url="https://example.com/owner/repo.git",
        branch="refs/heads/main",
        commit_id="abc123",
    )

    assert report.state == BuildStatus.ERROR
