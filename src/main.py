# REMOVE THIS ASAP: ADDED TO ALLOW BUILD FROM MAIN
# type: ignore
import threading

from flask import Flask, jsonify, request

from builder import build_project

app = Flask(__name__)


@app.route("/")
def home():
    return "CI Server is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("yoyoyfasasdfdod")

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
