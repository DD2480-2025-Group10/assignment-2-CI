from dataclasses import dataclass
from typing import Optional, Protocol
from enum import Enum

from src.models import BuildRef, BuildReport


class NotificationStatus(Enum):
    """Status of a notification attempt."""

    SENT = "sent"
    FAILED = "failed"


@dataclass(frozen=True)
class NotificationResult:
    """Result of a notification attempt.

    Attributes:
        status: Whether the notification was sent or failed.
        message: Optional error message if notification failed.
    """

    status: NotificationStatus
    message: Optional[str] = None


class Notifier(Protocol):
    """
    Interface for sending build status notifications back to the user.
    """

    def notify(self, ref: BuildRef, report: BuildReport) -> NotificationResult: ...
