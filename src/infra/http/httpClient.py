from typing import Any, Protocol, Dict, Optional


class HttpClient(Protocol):
    """
    Generic interface for making HTTP requests.
    """
    def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any: ...

    # More HTTP methods (get, put, delete, etc.) can be added as needed.
