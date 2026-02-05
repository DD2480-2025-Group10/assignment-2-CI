from flask import Flask, request, jsonify
from builder import build_project
import threading

app = Flask(__name__)


@app.route("/")
def home():
    return "CI Server is running!"


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

<<<<<<< issue-5
    return jsonify({"message": "Build started", "id": commit_id}), 201
=======
    return jsonify({"message": "Build started", "id": commit_id}), 200
>>>>>>> main


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
