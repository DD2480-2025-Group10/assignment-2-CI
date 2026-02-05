from typing import Any
from .httpClient import HttpClient
import requests

unkownDict = dict[str, Any]


class RequestsHttpClient(HttpClient):
    def post(
        self,
        url: str,
        data: unkownDict | None = None,
        json: unkownDict | None = None,
        **kwargs: Any,
    ) -> Any:
        return requests.post(url, data=data, json=json, **kwargs)
