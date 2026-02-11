from typing import Any, Dict, Optional
from src.infra.githubAuth.githubAuth import GithubAuth, GithubAuthContext
from src.infra.http.httpClient import HttpClient
from src.infra.http.requestsHttpClient import RequestsHttpClient
from .github import GithubNotificationTransport
from .exceptions import TransportError


class GithubRequestsTransport(GithubNotificationTransport):
    """HTTP transport for sending build status notifications to GitHub.

    Uses the requests library to post commit status updates to the GitHub API.

    Attributes:
        auth: GitHub authentication handler.
    """
    def __init__(self, auth: GithubAuth, client: Optional[HttpClient] = None) -> None:
        self.auth = auth
        self._client = client if client is not None else RequestsHttpClient()

    def create_commit_status(
        self, repo: str, sha: str, payload: Dict[str, Any], ctx: GithubAuthContext
    ) -> None:
        """Create a commit status on GitHub.

        Args:
            repo: Repository in format "owner/repo".
            sha: Commit SHA to update.
            payload: Status payload (state, description, context).
            ctx: GitHub authentication context.

        Raises:
            TransportError: If the API request fails.
        """
        url = f"https://api.github.com/repos/{repo}/statuses/{sha}"

        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            **self.auth.headers(ctx),
        }

        try:
            response = self._client.post(url, json=payload, headers=headers, timeout=50)
        except Exception as e:
            raise TransportError(f"Failed to create commit status: {str(e)}") from e

        if not response.ok:
            raise TransportError(
                f"Failed to create commit status: {response.status_code} {response.text}"
            )
