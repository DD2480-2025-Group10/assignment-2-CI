from typing import Mapping
from src.infra.githubAuth.githubAuth import GithubAuth, GithubAuthContext


class GithubAuthMock(GithubAuth):
    def headers(self, ctx: GithubAuthContext) -> Mapping[str, str]:
        return {"MockHeader": "MockValue"}
