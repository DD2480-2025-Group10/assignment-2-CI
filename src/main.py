# REMOVE THIS ASAP: ADDED TO ALLOW BUILD FROM MAIN
# type: ignore
from flask import Flask, request, jsonify
#from builder import build_project
from src.auth import create_github_auth
from src.adapters.notifier.github import GithubNotifier
from src.infra.notifier.requestsTransport import GithubRequestsTransport
import threading

from src.models import BuildRef

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
        return jsonify({"error": "Invalid payload, missing required fields", "payload": raw_request}), 401

    build_ref = BuildRef(**build_ref_raw)
    dummy_report = BuildReport(state=BuildStatus.SUCCESS, description="Test notification")

    result = NOTIFICATION_HANDLER.notify(build_ref, dummy_report)

    if result.status == NotificationStatus.SENT:
        return jsonify({"message": "Notification sent successfully"}), 200
    else: 
        return jsonify({"error": f"Failed to send notification: {result.message}"}), 500



@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if not data or "repository" not in data:
        return jsonify({"error": "Invalid payload"}), 400

    # https://docs.github.com/en/webhooks/webhook-events-and-payloads#push
    repo_url = data["repository"]["clone_url"]
    branch = data["ref"].replace("refs/heads/", "")
    commit_id = data["head_commit"]["id"]

    print(f"Get Webhook: Branch={branch}, ID={commit_id}")

    # Assume our builder looks like build_project(repo_url, branch, commit_id)
    thread = threading.Thread(target=build_project, args=(repo_url, branch, commit_id))
    thread.start()

    return jsonify({"message": "Build started", "id": commit_id}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
