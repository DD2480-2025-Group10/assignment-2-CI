from functools import wraps
from typing import Callable, Tuple
from flask import Flask, Response, jsonify
from datetime import datetime
from src.adapters.notifier.github import GithubNotifier

from src.auth import create_github_auth
from src.builder import build_project
from src.infra.githubAuth.githubAuth import GithubAuthContext
from src.infra.notifier.requestsTransport import GithubRequestsTransport
from src.input_validation import webhook_validation_factory
from src.models import BuildRef, BuildReport, BuildStatus, LogType, LogEntry
from src.ports.notifier import NotificationStatus
from src.view_history import list_logs, view_log, save_log_to_file


FlaskResponse = Tuple[Response, int]
NotifierMiddleware = Callable[[BuildRef], FlaskResponse]
CiHandler = Callable[[BuildRef], BuildReport]


def notifier_middleware_factory(
    notifier: GithubNotifier,
) -> Callable[[CiHandler], NotifierMiddleware]:
    """
    Middleware factory for creating a notifier middleware that sends notifications before and after
    the CI handler is executed.

    The middleware sends a "pending" notification before the CI handler is executed, and then sends
    success or failure notifications based on the result of the CI handler. If sending a notification fails,
    """

    def notify_middleware(f: CiHandler) -> NotifierMiddleware:
        @wraps(f)
        def middleware(ref: BuildRef) -> FlaskResponse:
            pending_report = BuildReport(
                state=BuildStatus.PENDING,
                description="Build is pending",
            )

            res = notifier.notify(ref, pending_report)
            if res.status != NotificationStatus.SENT:
                print(
                    f"[ERROR] Failed to send notification: \n\tPayload: {pending_report}\n\tError:{res.message}"
                )

            report = f(ref)

            res = notifier.notify(ref, report)
            if res.status != NotificationStatus.SENT:
                print(
                    f"[ERROR] Failed to send notification: \n\tPayload: {report}\n\tError:{res.message}"
                )

            return jsonify(
                {
                    "received": True,
                    "repo": ref.repo,
                    "sha": ref.sha,
                }
            ), 201

        return middleware

    return notify_middleware


def create_app() -> Flask:
    """
    Creates and configures the Flask application.

    Resposible for setting up routes, middleware, and initializing necessary components such
    as authentication handlers and notifiers.
    """
    app = Flask(__name__)

    AUTH_HANDLER = create_github_auth()
    NOTIFICATION_TRANSPORT = GithubRequestsTransport(AUTH_HANDLER)
    NOTIFICATION_HANDLER = GithubNotifier(NOTIFICATION_TRANSPORT)

    @app.route("/webhook", methods=["POST"])
    @webhook_validation_factory(AUTH_HANDLER)
    @notifier_middleware_factory(NOTIFICATION_HANDLER)
    def webhook(ref: BuildRef) -> BuildReport:
        # Stable clone URL with token authentication for GitHub
        # Allows cloning even private repositories
        clone_url = f"https://x-access-token:{
            AUTH_HANDLER.get_token(GithubAuthContext(ref.installation_id))
        }@github.com/{ref.repo}.git"
        report, log_str_gradle = build_project(ref.clone_url, ref.branch, ref.sha)

        log_entry = LogEntry(
            type=LogType.INFO if report.state == BuildStatus.SUCCESS else LogType.ERROR,
            repo_url=ref.clone_url,
            refspec=ref.ref,
            commit_SHA=ref.sha,
            date_time=datetime.now(),
            status=report.state,
            gradle_output=log_str_gradle,
        )
        save_log_to_file(log_entry)

        return report

    @app.route("/")
    def home() -> str:
        """Health check endpoint.

        Returns:
            Simple status message indicating the server is running.
        """
        return "CI Server is running!"

    @app.route("/logs")
    def list_logs_page() -> str:
        """
        Route handler for the build history dashboard.

        Triggers the retrieval of all log files and displays the summary list to the user.
        """
        return list_logs()

    @app.route("/logs/<filename>")
    def view_log_page(filename: str) -> str:
        """
        Route handler for individual build details.

        Fetches the specific log content based on the filename provided in the URL.

        Args:
            filename (str): The unique name of the log file to be displayed.
        """
        return view_log(filename)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8010, debug=True)
