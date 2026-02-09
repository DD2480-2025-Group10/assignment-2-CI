# REMOVE THIS ASAP: ADDED TO ALLOW BUILD FROM MAIN
# type: ignore
from flask import Flask, jsonify, request

from src.adapters.notifier.github import GithubNotifier

# from builder import build_project
from src.auth import create_github_auth
from src.builder import build_project
from src.infra.notifier.requestsTransport import GithubRequestsTransport
from src.models import BuildRef, BuildReport, BuildStatus
from src.payloads import PayloadValidationError, build_github_push_payload
from src.ports.notifier import NotificationStatus

app = Flask(__name__)

AUTH_HANDLER = create_github_auth()
NOTIFICATION_TRANSPORT = GithubRequestsTransport(AUTH_HANDLER)
NOTIFICATION_HANDLER = GithubNotifier(NOTIFICATION_TRANSPORT)


@app.route("/")
def home():
    return "CI Server is running!"


@app.route("/auth-notify-test", methods=["POST"])
def auth_notify_test():
    """
    Endpoint to test authentication and notification. Should be configured to be called
    as the webhook URL for the GitHub App. Can be removed after testing or transferred
    in a post request middleware.
    """
    raw_request = request.get_json() or {}

    build_ref_raw = {
        "repo": raw_request.get("repository", {}).get("full_name", None),
        "ref": raw_request.get("ref", None),
        "sha": raw_request.get("head_commit", {}).get("id", None),
        "installation_id": raw_request.get("installation", {}).get("id", None),
    }

    if not all(build_ref_raw.values()):
        return jsonify(
            {
                "error": "Invalid payload, missing required fields",
                "payload": raw_request,
            }
        ), 401

    build_ref = BuildRef(**build_ref_raw)
    dummy_report = BuildReport(
        state=BuildStatus.SUCCESS, description="Test notification"
    )

    result = NOTIFICATION_HANDLER.notify(build_ref, dummy_report)

    if result.status == NotificationStatus.SENT:
        return jsonify({"message": "Notification sent successfully"}), 200
    else:
        return jsonify({"error": f"Failed to send notification: {result.message}"}), 500


@app.route("/webhook", methods=["POST"])
def webhook():
    raw = request.get_json(silent=True) or {}

    try:
        payload = build_github_push_payload(raw)
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

    ref = BuildRef(
        repo=payload.repository_full_name,
        ref=payload.ref,
        sha=payload.head_commit_id,
    )

    print(ref)

    report = build_project(ref.repo, payload.branch, ref.sha)

    response_body = {
        "repo": ref.repo,
        "ref": ref.ref,
        "sha": ref.sha,
        "state": report,
        # "description": report.description, // lets add this later
    }

    status_code = 200 if report else 500

    return jsonify(response_body), status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
