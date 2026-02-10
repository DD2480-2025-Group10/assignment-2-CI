from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass
class GitHubPushPayload:
    repository_full_name: str
    ref: str
    head_commit_id: str

    @property
    def branch(self) -> str:
        return self.ref.removeprefix("refs/heads/")


class PayloadValidationError(Exception):
    def __init__(self, errors: list[str]) -> None:
        super().__init__("Invalid GitHub push payload")
        self.errors = errors


def build_github_push_payload(raw: Mapping[str, Any]) -> GitHubPushPayload:
    errors: list[str] = []

    repository = raw.get("repository")
    if not isinstance(repository, Mapping):
        errors.append("'repository' must be an object")
        repository = None

    ref = raw.get("ref")
    if not isinstance(ref, str) or not ref.startswith("refs/heads/"):
        errors.append("'ref' must be a branch ref like 'refs/heads/main'")

    head_commit = raw.get("head_commit")
    if not isinstance(head_commit, Mapping):
        errors.append("'head_commit' must be an object")
        head_commit = None

    repository_full_name: str | None = None
    if isinstance(repository, Mapping):
        repository_full_name = repository.get("ssh_url")
        if not isinstance(repository_full_name, str) or not repository_full_name:
            errors.append("'repository.ssh_url' must be a non-empty string")

    head_commit_id: str | None = None
    if isinstance(head_commit, Mapping):
        head_commit_id = head_commit.get("id")
        if not isinstance(head_commit_id, str) or not head_commit_id:
            errors.append("'head_commit.id' must be a non-empty string")

    if errors:
        raise PayloadValidationError(errors)

    return GitHubPushPayload(
        repository_full_name=repository_full_name,
        ref=ref,
        head_commit_id=head_commit_id,
    )
