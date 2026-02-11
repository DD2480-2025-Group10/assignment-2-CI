"""
The ports module defines generic contracts for external interactions, such as notifications. 

This allows the core logic of the CI server to be decoupled from specific implementations of these interactions, 
making it easier to swap out different notification mechanisms (e.g., GitHub commit statuses, email notifications, etc.) 
without affecting the core functionality of the server.
"""
from .notifier import Notifier, NotificationResult, NotificationStatus
