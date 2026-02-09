from typing import Tuple
from src.infra.githubAuth.appAuth import GithubAppAuth, GithubAppConfig
from tests.mocks.httpClientMock import MockHttpClient
from tests.mocks.clockMock import ClockMock
import pytest

from src.infra.notifier.exceptions import TransportError
from src.infra.githubAuth.githubAuth import GithubAuthContext
from src.infra.githubAuth.appAuth import GithubAppAuth, GithubAppConfig


def generate_jwt_mock(jwt: str = "mock_jwt", exp: int = 0):
    def mock() -> Tuple[str, int]:
        return jwt, exp

    return mock


def test_jwt_claims():
    appConfig = GithubAppConfig(client_id="mock", private_key_pem="key")
    client = MockHttpClient(response_ok=True)
    clock = ClockMock(fixed_time=0)
    auth = GithubAppAuth(config=appConfig, client=client, clock=clock)

    claims = auth._get_claims()

    assert claims["iss"] == "mock"
    assert claims["iat"] == -30
    assert 0 < claims["exp"] and claims["exp"] < 10 * 60


def test_jwt_caching():
    appConfig = GithubAppConfig(client_id="mock", private_key_pem="key")
    client = MockHttpClient(response_ok=True)
    clock = ClockMock(fixed_time=0)
    auth = GithubAppAuth(config=appConfig, client=client, clock=clock)

    # Should not cache, expires instantly
    auth._generate_jwt = generate_jwt_mock(jwt="not cached")
    token1 = auth._get_jwt()
    # Should be cached
    auth._generate_jwt = generate_jwt_mock(jwt="cached", exp=1000)
    token2 = auth._get_jwt()

    assert token1 != token2
    assert token2 == auth._get_jwt()  # Should return cached token


def test_headers_requires_installation_id():
    appConfig = GithubAppConfig(client_id="mock", private_key_pem="key")
    client = MockHttpClient(response_ok=True)
    clock = ClockMock(fixed_time=0)
    auth = GithubAppAuth(config=appConfig, client=client, clock=clock)

    with pytest.raises(TransportError):
        auth.headers(GithubAuthContext(installation_id=None))


def test_headers_returns_bearer_token_from_installation_token():
    appConfig = GithubAppConfig(client_id="mock", private_key_pem="key")
    client = MockHttpClient(
        response_ok=True,
        raise_exception=False,
        response_json={"token": "inst_token_1", "expires_at": "2030-01-01T00:00:00Z"},
    )
    clock = ClockMock(fixed_time=0)
    auth = GithubAppAuth(config=appConfig, client=client, clock=clock)

    auth._get_jwt = lambda: "mock_jwt"

    hdrs = auth.headers(GithubAuthContext(installation_id=123))
    assert hdrs["Authorization"] == "Bearer inst_token_1"


def test_installation_token_is_cached_and_http_called_once():
    appConfig = GithubAppConfig(client_id="mock", private_key_pem="key")
    client = MockHttpClient(
        response_ok=True,
        raise_exception=False,
        response_json={"token": "inst_token_1", "expires_at": "2030-01-01T00:00:00Z"},
    )
    clock = ClockMock(fixed_time=0)
    auth = GithubAppAuth(config=appConfig, client=client, clock=clock)
    auth._get_jwt = lambda: "mock_jwt"

    # First call fetches
    hdrs1 = auth.headers(GithubAuthContext(installation_id=123))
    # Second call should hit cache (expires far in future)
    hdrs2 = auth.headers(GithubAuthContext(installation_id=123))

    assert hdrs1["Authorization"] == "Bearer inst_token_1"
    assert hdrs2["Authorization"] == "Bearer inst_token_1"
    assert client.called_times == 1


def test_fetch_installation_token_raises_on_http_error_response():
    appConfig = GithubAppConfig(client_id="mock", private_key_pem="key")
    client = MockHttpClient(response_ok=False)
    clock = ClockMock(fixed_time=0)
    auth = GithubAppAuth(config=appConfig, client=client, clock=clock)
    auth._get_jwt = lambda: "mock_jwt"

    with pytest.raises(TransportError):
        auth._fetch_installation_token(installation_id=123)


def test_fetch_installation_token_raises_on_client_exception():
    appConfig = GithubAppConfig(client_id="mock", private_key_pem="key")
    client = MockHttpClient(raise_exception=True)
    clock = ClockMock(fixed_time=0)
    auth = GithubAppAuth(config=appConfig, client=client, clock=clock)
    auth._get_jwt = lambda: "mock_jwt"

    with pytest.raises(TransportError):
        auth._fetch_installation_token(installation_id=123)
