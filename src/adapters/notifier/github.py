from src.infra.githubAuth.githubAuth import GithubAuthContext
from src.infra.notifier.exceptions import TransportError
from src.infra.notifier.github import GithubNotificationTransport
from src.models import BuildRef, BuildReport
from src.ports.notifier import NotificationResult, NotificationStatus, Notifier


class GithubNotifier(Notifier):
    """
    The GithubNotifier implements the Notifier interface to send build notifications to
    Github using the provided transport.

    The constructor accepts a GithubNotificationTransport, which is responsible for
    inteacting with the Github API.

    If no Transport is provided, it defaults to using the GithubRequestsTransport with
    authentication via a Personal Access Token (PAT) retrieved from the environment
    variable "GITHUB_PAT".
    """

    def __init__(self, transport: GithubNotificationTransport) -> None:
        self.transport = transport

    def notify(self, ref: BuildRef, report: BuildReport) -> NotificationResult:
        payload = {
            "state": report.state.value,
            "description": report.description,
            "context": report.context,
        }
        try:
            ctx = GithubAuthContext(installation_id=ref.installation_id)
            self.transport.create_commit_status(ref.repo, ref.sha, payload, ctx)
            return NotificationResult(status=NotificationStatus.SENT)
        except TransportError as e:
            return NotificationResult(status=NotificationStatus.FAILED, message=str(e))
