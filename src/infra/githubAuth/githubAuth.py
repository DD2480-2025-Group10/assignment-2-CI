from dataclasses import dataclass
from typing import Mapping, Optional, Protocol


@dataclass(frozen=True)
class GithubAuthContext:
    installation_id: Optional[int] = None


class GithubAuth(Protocol):
    def headers(self, ctx: GithubAuthContext) -> Mapping[str, str]:
        """
        Returns the headers required for authenticating with the GitHub API.
        """
        ...
