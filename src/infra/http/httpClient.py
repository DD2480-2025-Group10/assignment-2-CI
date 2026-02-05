from typing import Any, Protocol 

unkownDict = dict[str, Any]

class HttpClient(Protocol):
    def post(self, url: str, data: unkownDict | None = None, json: unkownDict | None = None, **kwargs: Any) -> Any:
        ...

    # More HTTP methods (get, put, delete, etc.) can be added as needed.
