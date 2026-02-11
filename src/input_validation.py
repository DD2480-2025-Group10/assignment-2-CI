from collections.abc import Mapping
from typing import Any, Optional, cast

from src.models import BuildRef


class PayloadValidationError(Exception):
    """Exception raised when a GitHub webhook payload is invalid.

    Attributes:
        errors: List of validation error messages.
    """

    def __init__(self, errors: list[str]) -> None:
        super().__init__("Invalid GitHub push payload")
        self.errors = errors


def build_github_push_payload(raw: Mapping[str, Any]) -> BuildRef:
    """Parse and validate a GitHub push webhook payload.

    Args:
        raw: Raw JSON payload from GitHub webhook.

    Returns:
        Validated BuildRef object.

    Raises:
        PayloadValidationError: If required fields are missing.
    """
    errors: list[str] = []

    full_name: Optional[str] = raw.get("repository", {}).get("full_name", None)
    ref: Optional[str] = raw.get("ref")
    head_sha: Optional[str] = raw.get("head_commit", {}).get("id", None)
    installation_id: Optional[int] = raw.get("installation", {}).get("id", None)

    if full_name is None:
        errors.append("Payload missing 'repository.full_name' field")

    if ref is None:
        errors.append("Payload missing 'ref' field")

    if head_sha is None:
        errors.append("Payload missing 'head_commit.id' field")

    if installation_id is None:
        errors.append("Payload missing 'installation.id' field")

    if len(errors) > 0:
        raise PayloadValidationError(errors)

    return BuildRef(
        repo=str(full_name),
        ref=str(ref),
        sha=str(head_sha),
        installation_id=cast(int, installation_id),
    )
