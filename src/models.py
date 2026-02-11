from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class BuildRef:
    """
    Reference to a build triggered by a wehbook event.

    Attributes:
        repo (str): The repository's full_name field from the webhook payload.
                    (e.g., "owner/repo")
        ref (str):  The git reference of the commit to build (e.g., "refs/heads/main" or "refs/tags/v1.0").
                    Losely equivalent to what branch the event was triggered on.
        sha (str):  The full commit SHA of the commit to build.
        installation_id (Optional[int]): The GitHub App installation ID if the event was triggered by a
                        GitHub App installation.

    Source: https://gist.github.com/walkingtospace/0dcfe43116ca6481f129cdaa0e112dc4
    Note:   The github documentation does not specify the exact format of the repository
            field, and hence how the repo field is derived should be clarified.
    """

    repo: str
    ref: str
    sha: str
    installation_id: int | None = None

    @property
    def branch(self) -> str:
        """
        Extracts the branch name from the ref field.
        For example, if ref is "refs/heads/main", this will return "main".
        If ref is "refs/tags/v1.0", this will return "v1.0".
        Returns:
            str: The extracted branch or tag name.
        """
        return self.ref.removeprefix("refs/heads/")

    @property
    def ssh_url(self) -> str:
        """
        Constructs the SSH URL for the repository based on the repo field.
        For example, if repo is "owner/repo", this will return
        "git@github.com:owner/repo.git".
        """
        return f"git@github.com:{self.repo}.git"

    @property
    def clone_url(self) -> str:
        """HTTPS URL FOR CLONING REPO"""
        return f"https://github.com/{self.repo}.git"


class BuildStatus(str, Enum):
    """
    Enumeration of possible build statuses.
    """

    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"
    ERROR = "error"


@dataclass(frozen=True)
class BuildReport:
    """
    Report indicating the status of a build to be sent back to the user.

    Attributes:
        state (BuildStatus): The status of the build (e.g., success, failure, pending, error).
        target_url (Optional[str]): An optional URL pointing to the build logs or details.
        description (Optional[str]): An optional description providing more context about the build status.
        context (str): A string label to differentiate this status from others (default: "Group 10 CI/CD Pipeline").
    """

    state: BuildStatus
    target_url: str | None = None
    description: str | None = None
    context: str = "Group 10 CI/CD Pipeline"
