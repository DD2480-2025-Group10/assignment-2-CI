"""
Github authentication module.

Provides one generic interface for authenticating against github, and
multiple implementations for different authentication methods (e.g. Github App, Personal Access Token).
"""

from .appAuth import GithubAppAuth, GithubAppConfig
from .githubAuth import GithubAuth, GithubAuthContext
from .patAuth import GithubPatAuth
