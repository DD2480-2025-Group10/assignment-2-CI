"""
This module provides neccesary interfaces for sending notifications to external services (so called "transports")

The the transports in this module are responsible for the sending part of notifications, while the adapters are 
responsible for what to send.
"""
from .exceptions import TransportError
from .github import GithubNotificationTransport
from .requestsTransport import GithubRequestsTransport
