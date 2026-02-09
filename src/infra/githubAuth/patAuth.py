from typing import Mapping
from .githubAuth import GithubAuth, GithubAuthContext


class GithubPatAuth(GithubAuth):
    def __init__(self, token: str) -> None:
        self.token = token

    def headers(self, ctx: GithubAuthContext) -> Mapping[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
        }

    def get_token(self, ctx: GithubAuthContext) -> str:
        return self.token
