from dataclasses import dataclass, field
from typing import Any
from src.infra.http.httpClient import HttpClient


@dataclass
class MockResponse:
    ok: bool
    text: str = "Mock response text"
    status_code: int = 200
    response_json: dict[str, Any] = field(default_factory=dict)

    def json(self) -> dict[str, Any]:
        return self.response_json


class MockHttpClient(HttpClient):
    def __init__(
        self,
        response_ok: bool = True,
        raise_exception: bool = False,
        response_json: dict[str, Any] = {},
    ) -> None:
        self.response_ok = response_ok
        self.response_json = response_json
        self.called_times = 0
        self.last_url: str = ""
        self.last_data: dict[str, Any] = {}
        self.last_headers: dict[str, Any] = {}
        self.raise_exception = raise_exception

    def post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        self.called_times += 1
        self.last_url = url
        self.last_data = json if json is not None else data if data is not None else {}
        self.last_headers = kwargs.get("headers", {})

        if self.raise_exception:
            raise Exception("Mock exception")

        return MockResponse(
            ok=self.response_ok,
            text="Mock response text",
            status_code=200,
            response_json=self.response_json,
        )
