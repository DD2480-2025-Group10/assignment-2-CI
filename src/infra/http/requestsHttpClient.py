from typing import Any, Dict, Optional
from .httpClient import HttpClient
import requests

unkownDict = Optional[Dict[str, Any]]


class RequestsHttpClient(HttpClient):
    """
    Concrete implementation of HttpClient using the requests library.
    """

    def post(
        self,
        url: str,
        data: unkownDict = None,
        json: unkownDict = None,
        **kwargs: Any,
    ) -> Any:
        return requests.post(url, data=data, json=json, **kwargs)
