from dataclasses import dataclass
from typing import Any, Dict, Mapping, Tuple
import time
import jwt
from .githubAuth import GithubAuth, GithubAuthContext
from src.infra.http.httpClient import HttpClient
from src.infra.http.requestsHttpClient import RequestsHttpClient
from src.infra.notifier.exceptions import TransportError
from src.infra.time.clock import Clock, SystemClock


@dataclass(frozen=True)
class GithubAppConfig:
    """
    Dataclass representing the neccessary configuration for authenticating as a GitHub App.
    This includes the app's identifier and the PEM-encoded private key used for signing JWTs.
    """

    app_id: str
    private_key_pem: str


@dataclass(frozen=True)
class GithubTokenResponse:
    token: str
    expires_at: int


class GithubAppAuth(GithubAuth):
    def __init__(
        self,
        config: GithubAppConfig,
        client: HttpClient | None = None,
        clock: Clock | None = None,
    ) -> None:
        self.cfg = config
        self._client = RequestsHttpClient() if client is None else client
        self._clock = clock if clock is not None else SystemClock()
        self._jwt_cache: Tuple[str, int] | None = (
            None  # Cache for JWT tokens with their expiration times
        )
        self._installation_token_cache: Dict[int, GithubTokenResponse] = {}

    def headers(self, ctx: GithubAuthContext) -> Mapping[str, str]:
        if ctx.installation_id is None:
            raise TransportError(
                "Installation ID is required for GitHub App authentication"
            )

        token = self._get_installation_token(ctx.installation_id)
        return {
            "Authorization": f"Bearer {token}",
        }

    def get_token(self, ctx: GithubAuthContext) -> str:
        if ctx.installation_id is None:
            raise TransportError(
                "Installation ID is required for GitHub App authentication"
            )
        return self._get_installation_token(ctx.installation_id)

    def _get_claims(self) -> dict[str, Any]:
        now = int(self._clock.time())
        return {
            "iat": now
            - 30,  # issued 30 seconds in the past to allow deviations in time
            "exp": now
            + 9 * 60,  # 9 minutes expiration (max 10 minutes allowed by GitHub)
            "iss": self.cfg.app_id,
        }

    def _generate_jwt(self) -> Tuple[str, int]:
        """
        Generates a JWT for authenticating as a GitHub App.
        """
        payload = self._get_claims()
        jwt_token = jwt.encode(payload, self.cfg.private_key_pem, algorithm="RS256")

        return jwt_token, payload["exp"]

    def _get_jwt(self) -> str:
        """
        Retrieves a cached JWT or generates a new one if the cached one is expired or absent.
        """
        now = int(self._clock.time())

        if self._jwt_cache is not None:
            cached_jwt, exp = self._jwt_cache

            if exp > now + 60:
                return cached_jwt

        jwt_token, exp = self._generate_jwt()
        self._jwt_cache = (jwt_token, exp)

        return jwt_token

    def _get_installation_token(self, installation_id: int) -> str:
        """
        Retrieves an installation access token for the given installation ID.
        """
        now = int(self._clock.time())

        # Check cache for valid token
        cached_token = self._installation_token_cache.get(installation_id)
        if cached_token is not None and cached_token.expires_at > now + 60:
            return cached_token.token

        # Delete expired token from cache if it existed
        self._installation_token_cache.pop(installation_id, None)

        token_response = self._fetch_installation_token(installation_id)

        self._installation_token_cache[installation_id] = token_response
        return token_response.token

    def _fetch_installation_token(self, installation_id: int) -> GithubTokenResponse:
        """
        Mints a new installation access token for the given installation ID.
        from the GitHub API.
        """

        url = (
            f"https://api.github.com/app/installations/{installation_id}/access_tokens"
        )
        jwt_token = self._get_jwt()
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        # Calls the GitHub API to create an installation token
        try:
            response = self._client.post(url, headers=headers, timeout=30)
        except Exception as e:
            raise TransportError(f"Failed to obtain installation token: {e}") from e

        if not response.ok:
            raise TransportError(
                f"Failed to obtain installation token: {response.status_code} {response.text}"
            )

        token_data = response.json()
        token_response = GithubTokenResponse(
            token=token_data["token"],
            expires_at=_parse_github_datetime(token_data["expires_at"]),
        )
        return token_response


def _parse_github_datetime(dt_str: str) -> int:
    dt = time.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ")
    return int(time.mktime(dt))
