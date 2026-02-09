# REMOVE THIS ASAP: ADDED TO ALLOW BUILD FROM MAIN
# type: ignore

from flask import Flask, jsonify, request

from payloads import PayloadValidationError, build_github_push_payload
from src.builder import build_project
from src.models import BuildRef

app = Flask(__name__)


@app.route("/")
def home():
    return "CI Server is running!"


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
