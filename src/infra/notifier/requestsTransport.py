from typing import Any
from src.infra.githubAuth.githubAuth import GithubAuth, GithubAuthContext
from src.infra.http.httpClient import HttpClient
from src.infra.http.requestsHttpClient import RequestsHttpClient
from .github import GithubNotificationTransport
from .exceptions import TransportError


class GithubRequestsTransport(GithubNotificationTransport):
    def __init__(self, auth: GithubAuth, client: HttpClient | None = None) -> None:
        self.auth = auth
        self._client = client if client is not None else RequestsHttpClient()

    def create_commit_status(
        self, repo: str, sha: str, payload: dict[str, Any], ctx: GithubAuthContext
    ) -> None:
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
