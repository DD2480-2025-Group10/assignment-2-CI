from src.infra.githubAuth.githubAuth import GithubAuthContext
from src.infra.notifier.exceptions import TransportError
from src.infra.notifier.requestsTransport import GithubRequestsTransport
from tests.mocks.httpClientMock import MockHttpClient
from tests.mocks.githubAuthMock import GithubAuthMock


def test_responese_ok():
    auth = GithubAuthMock()
    client = MockHttpClient(response_ok=True)
    transport = GithubRequestsTransport(auth, client)
    ctx = GithubAuthContext(None)

    transport.create_commit_status("owner/repo", "sha", {"state": "success"}, ctx)

    assert client.called_times > 0
    assert client.last_url == "https://api.github.com/repos/owner/repo/statuses/sha"
    assert client.last_data == {"state": "success"}
    assert client.last_headers.get("MockHeader") == "MockValue"


def test_response_not_ok():
    auth = GithubAuthMock()
    client = MockHttpClient(response_ok=False)
    transport = GithubRequestsTransport(auth, client)
    ctx = GithubAuthContext(None)

    try:
        transport.create_commit_status("owner/repo", "sha", {"state": "failure"}, ctx)
        assert False, "Expected TransportError was not raised"
    except TransportError as _:
        assert True


def test_client_exception():
    auth = GithubAuthMock()
    client = MockHttpClient(response_ok=True, raise_exception=True)
    transport = GithubRequestsTransport(auth, client)
    ctx = GithubAuthContext(None)

    try:
        transport.create_commit_status("owner/repo", "sha", {"state": "error"}, ctx)
        assert False, "Expected TransportError was not raised"
    except TransportError as _:
        assert True
