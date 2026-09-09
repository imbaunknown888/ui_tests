from typing import Any, TypeVar

import requests
from swagger_coverage_tool import SwaggerCoverageTracker

from src.main.api.configs.config import Config
from src.main.api.models.base_model import BaseModel
from src.main.api.requests.skeleton.http_request import HttpRequest
from src.main.api.requests.skeleton.interfaces.crud_end_interface import (
    CrudEndpointInterface,
)

T = TypeVar('T', bound=BaseModel)
tracker = SwaggerCoverageTracker(service="nbank-api")


class CrudRequester(HttpRequest, CrudEndpointInterface):
    @property
    def base_url(self) -> str:
        return f"{Config.get('server')}{Config.get('apiVersion')}"

    @property
    def timeout(self) -> float:
        return float(Config.get("REQUEST_TIMEOUT", 10))

    def _coverage_path(self, id: int | None = None) -> str:
        path = f"{Config.get('apiVersion')}{self.endpoint.value.url}"
        return f"{path}/{{id}}" if id is not None else path

    def _send(
        self,
        method: str,
        path_suffix: str = "",
        json: Any = None,
        coverage_id: int | None = None,
    ) -> requests.Response:
        @tracker.track_coverage_requests(self._coverage_path(coverage_id))
        def send_request() -> requests.Response:
            return requests.request(
                method=method,
                url=f"{self.base_url}{self.endpoint.value.url}{path_suffix}",
                headers=self.request_spec,
                json=json,
                timeout=self.timeout,
            )

        response = send_request()
        self.response_spec(response)
        return response

    def post(self, model: T | None = None) -> requests.Response:
        body = model.model_dump() if model is not None else None
        return self._send("POST", json=body)

    def get(self, id: int | None = None) -> requests.Response:
        path_suffix = f"/{id}" if id is not None else ""
        return self._send("GET", path_suffix=path_suffix, coverage_id=id)

    def update(self, model: BaseModel, id: int | None = None) -> requests.Response:
        body = model.model_dump() if model is not None else None
        path_suffix = f"/{id}" if id is not None else ""
        return self._send("PUT", path_suffix=path_suffix, json=body, coverage_id=id)

    def delete(self, id: int) -> requests.Response:
        return self._send("DELETE", path_suffix=f"/{id}", coverage_id=id)
