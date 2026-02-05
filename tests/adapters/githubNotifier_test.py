from typing import Any, Tuple

from src.adapters.notifier.github import GithubNotifier
from src.infra.notifier.exceptions import TransportError
from src.infra.githubAuth.githubAuth import GithubAuthContext
from src.models import BuildRef, BuildReport, BuildStatus
from src.ports.notifier import NotificationStatus


class FakeTransport:
    def __init__(self, *, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.calls: list[Tuple[str, str, dict[str, Any], GithubAuthContext]] = []

    def create_commit_status(
        self, repo: str, sha: str, payload: dict[str, Any], ctx: GithubAuthContext
    ) -> None:
        if self.should_fail:
            raise TransportError()
        self.calls.append((repo, sha, payload, ctx))


def test_notify_success_sends_commit_status_and_returns_sent():
    transport = FakeTransport(should_fail=False)
    notifier = GithubNotifier(transport=transport)

    ref = BuildRef(
        repo="owner/repo", ref="refs/heads/mock", sha="abc123", installation_id=42
    )
    report = BuildReport(
        state=BuildStatus.SUCCESS, description="ok", context="dd2480/ci"
    )

    result = notifier.notify(ref, report)

    assert result.status == NotificationStatus.SENT
    assert len(transport.calls) == 1

    repo, sha, payload, ctx = transport.calls[0]
    assert repo == "owner/repo"
    assert sha == "abc123"
    assert payload == {
        "state": report.state,
        "description": report.description,
        "context": report.context,
    }
    assert ctx.installation_id == 42


def test_notify_transport_error_returns_failed_with_message():
    transport = FakeTransport(should_fail=True)
    notifier = GithubNotifier(transport=transport)

    ref = BuildRef(
        repo="owner/repo", ref="refs/heads/mock", sha="abc123", installation_id=42
    )
    report = BuildReport(
        state=BuildStatus.FAILURE, description="tests failed", context="dd2480/ci"
    )

    result = notifier.notify(ref, report)

    assert result.status == NotificationStatus.FAILED
    assert len(transport.calls) == 0
