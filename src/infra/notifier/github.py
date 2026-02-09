from typing import Any, Protocol, Dict
from src.infra.githubAuth.githubAuth import GithubAuthContext


class GithubNotificationTransport(Protocol):
    """
    Interface for sending build status notifications back to GitHub by creating commit statuses.

    Exeptions:
        TransportError: Raised when a transport error occurs while sending a notification.
    """

    def create_commit_status(
        self, repo: str, sha: str, payload: Dict[str, Any], ctx: GithubAuthContext
    ) -> None: ...
