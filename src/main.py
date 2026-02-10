from typing import Tuple
from flask import Flask, Response, jsonify, request

from src.adapters.notifier.github import GithubNotifier

from src.auth import create_github_auth
from src.builder import build_project
from src.infra.notifier.requestsTransport import GithubRequestsTransport
from src.input_validation import PayloadValidationError, build_github_push_payload
from src.models import BuildReport, BuildStatus
from src.ports.notifier import NotificationStatus


app = Flask(__name__)

AUTH_HANDLER = create_github_auth()
NOTIFICATION_TRANSPORT = GithubRequestsTransport(AUTH_HANDLER)
NOTIFICATION_HANDLER = GithubNotifier(NOTIFICATION_TRANSPORT)


@app.route("/")
def home() -> str:
    return "CI Server is running!"


@app.route("/webhook", methods=["POST"])
def webhook() -> Tuple[Response, int]:
    raw = request.get_json(silent=True) or {}

    try:
        ref = build_github_push_payload(raw)
    except PayloadValidationError as exc:
        return (
            jsonify(
                {
                    "error": "Invalid payload",
                    "details": exc.errors,
                }
            ),
            400,
        )

    pending_report = BuildReport(
        state=BuildStatus.PENDING,
        description="Build is pending",
    )

    res = NOTIFICATION_HANDLER.notify(ref, pending_report)
    if res.status != NotificationStatus.SENT:
        print(f"Failed to send pending notification: {res.message}")

    report = build_project(ref.ssh_url, ref.branch, ref.sha)

    res = NOTIFICATION_HANDLER.notify(ref, report)
    if res.status != NotificationStatus.SENT:
        print(f"Failed to send final notification: {res.message}")

    response_body = {
        "repo": ref.repo,
        "ref": ref.ref,
        "sha": ref.sha,
        "status": report,
    }

    status_code = 200 if report else 500

    return jsonify(response_body), status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
