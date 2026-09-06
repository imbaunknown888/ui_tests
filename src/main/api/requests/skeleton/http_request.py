from collections.abc import Callable
from typing import Protocol

from src.main.api.requests.skeleton.endpoint import Endpoint


class HttpRequest(Protocol):
    def __init__(
        self,
        request_spec: dict[str, str],
        endpoint: Endpoint,
        response_spec: Callable
    ):
        self.request_spec = request_spec
        self.endpoint = endpoint
        self.response_spec = response_spec
