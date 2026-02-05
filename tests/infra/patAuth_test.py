from src.infra.githubAuth import GithubPatAuth, GithubAuthContext


def test_pat_valid_header():
    auth = GithubPatAuth("my-token")
    ctx = GithubAuthContext(None)

    headers = auth.headers(ctx)

    assert headers.keys() == {"Authorization"}
    assert headers["Authorization"] == "Bearer my-token"
