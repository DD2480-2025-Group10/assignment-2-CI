from functools import wraps
from typing import Optional, ParamSpec, Tuple, Callable, TypeVar
from src.infra.githubAuth.appAuth import GithubAppAuth
from pydantic import BaseModel
from flask import request, jsonify, Response

from src.infra.githubAuth.githubAuth import GithubAuth
from src.models import BuildRef


class RepositoryPayload(BaseModel):
    """
    Pydantic model for the repository information in the GitHub webhook payload.
    """
    full_name: str


class InstallationPayload(BaseModel):
    """
    Pydantic model for the installation information in the GitHub webhook payload, 
    relevant for GitHub App authentication.
    """
    id: int


class HeadCommitPayload(BaseModel):
    """
    Pydantic model for the head commit information in the GitHub webhook payload.
    """
    id: str


class WebhookPayload(BaseModel):
    """
    Pydantic model for all the relevant information from the GitHub webhook payload 
    that is needed for processing.
    """
    repository: RepositoryPayload
    head_commit: HeadCommitPayload
    ref: str
    installation: Optional[InstallationPayload] = None


FlaskResponse = Tuple[Response, int]
WebhookHandler = Callable[[BuildRef], FlaskResponse]
InputValidator = Callable[[], FlaskResponse]


def webhook_validation_factory(
    auth_handler: GithubAuth,
) -> Callable[[WebhookHandler], InputValidator]:
    """
    Factory wrapper for validating incoming GitHub webhook payloads and extracting necessary information

    Validation differs based on the authentication method used. For GitHub App authentication, the payload 
    must include installation information, while for PAT authentication, this is not required. The factory 
    ensures that the payload is correctly parsed and validated according to the expected structure.

    The returned decorator can be applied to a webhook handler function that takes a `BuildRef` as input and 
    returns a Flask response. 
    """
    def decorator(f: WebhookHandler) -> InputValidator:
        @wraps(f)
        def wrapper() -> FlaskResponse:
            try:
                payload = request.get_json(silent=True) or {}
                body = WebhookPayload.model_validate(payload)
            except Exception as exc:
                print(f"[ERROR] Failed to parse webhook payload: {exc}")
                return (
                    jsonify(
                        {
                            "error": "Invalid payload",
                            "details": str(exc),
                        }
                    ),
                    400,
                )

            if isinstance(auth_handler, GithubAppAuth) and body.installation is None:
                print(
                    "[ERROR] Missing installation information for GitHub App authentication"
                )
                return (
                    jsonify(
                        {
                            "error": "Missing installation information for GitHub App authentication",
                        }
                    ),
                    422,
                )

            ref = BuildRef(
                repo=body.repository.full_name,
                ref=body.ref,
                sha=body.head_commit.id,
                installation_id=body.installation.id if body.installation else None,
            )

            return f(ref)

        return wrapper

    return decorator
