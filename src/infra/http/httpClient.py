from typing import Any, Protocol


class HttpClient(Protocol):
    def post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any: ...

    # More HTTP methods (get, put, delete, etc.) can be added as needed.
