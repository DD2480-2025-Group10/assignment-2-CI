from functools import wraps
from typing import Optional, ParamSpec, Tuple, Callable, TypeVar
from src.infra.githubAuth.appAuth import GithubAppAuth
from pydantic import BaseModel
from flask import request, jsonify, Response

from src.infra.githubAuth.githubAuth import GithubAuth
from src.models import BuildRef


class RepositoryPayload(BaseModel):
    full_name: str


class InstallationPayload(BaseModel):
    id: int


class HeadCommitPayload(BaseModel):
    id: str


class WebhookPayload(BaseModel):
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
