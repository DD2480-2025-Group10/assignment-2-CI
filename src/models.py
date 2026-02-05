from dataclasses import dataclass
from enum import Enum
from typing import Optional

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
    installation_id: Optional[int] = None

class BuildStatus(Enum):
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
    target_url: Optional[str] = None
    description: Optional[str] = None
    context: str = "Group 10 CI/CD Pipeline"


