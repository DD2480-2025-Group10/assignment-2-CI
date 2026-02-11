from functools import wraps
from typing import Callable, Tuple
from flask import Flask, Response, jsonify

from src.adapters.notifier.github import GithubNotifier

from src.auth import create_github_auth
from src.builder import build_project
from src.infra.githubAuth.githubAuth import GithubAuthContext
from src.infra.notifier.requestsTransport import GithubRequestsTransport
from src.input_validation import webhook_validation_factory 
from src.models import BuildRef, BuildReport, BuildStatus
from src.ports.notifier import NotificationStatus


app = Flask(__name__)

AUTH_HANDLER = create_github_auth()
NOTIFICATION_TRANSPORT = GithubRequestsTransport(AUTH_HANDLER)
NOTIFICATION_HANDLER = GithubNotifier(NOTIFICATION_TRANSPORT)

@app.route("/")
def home() -> str:
    """Health check endpoint.

    Returns:
        Simple status message indicating the server is running.
    """
    return "CI Server is running!"

FlaskResponse = Tuple[Response, int]
NotifierMiddleware = Callable[[BuildRef], FlaskResponse]
CiHandler = Callable[[BuildRef], BuildReport]

def notifier_middleware_factory(notifier: GithubNotifier) -> Callable[[CiHandler], NotifierMiddleware]:
    def notify_middleware(f: CiHandler) -> NotifierMiddleware:
        @wraps(f)
        def middleware(ref: BuildRef) -> FlaskResponse:
            pending_report = BuildReport(
                state=BuildStatus.PENDING,
                description="Build is pending",
            )

            res = notifier.notify(ref, pending_report)
            if res.status != NotificationStatus.SENT:
                print(f"[ERROR] Failed to send notification: \n\tPayload: {pending_report}\n\tError:{res.message}")

            report = f(ref)

            res = notifier.notify(ref, report)
            if res.status != NotificationStatus.SENT:
                print(f"[ERROR] Failed to send notification: \n\tPayload: {report}\n\tError:{res.message}")

            return jsonify({
                "received": True,
                "repo": ref.repo,
                "sha": ref.sha,
            }), 201

        return middleware
    return notify_middleware

@app.route("/webhook", methods=["POST"])
@webhook_validation_factory(AUTH_HANDLER)
@notifier_middleware_factory(NOTIFICATION_HANDLER)
def webhook(ref: BuildRef) -> BuildReport:
    # Stable clone URL with token authentication for GitHub 
    # Allows cloning even private repositories
    clone_url = f"https://x-access-token:{AUTH_HANDLER.get_token(
                                            GithubAuthContext(ref.installation_id)
                                        )}@github.com/{ref.repo}.git"
    report, log = build_project(clone_url, ref.branch, ref.sha)
    return report


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8010, debug=True)
