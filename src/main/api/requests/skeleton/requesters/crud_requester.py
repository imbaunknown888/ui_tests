from typing import Any, TypeVar

import requests

from src.main.api.configs.config import Config
from src.main.api.models.base_model import BaseModel
from src.main.api.requests.skeleton.http_request import HttpRequest
from src.main.api.requests.skeleton.interfaces.crud_end_interface import (
    CrudEndpointInterface,
)

T = TypeVar('T', bound=BaseModel)


class CrudRequester(HttpRequest, CrudEndpointInterface):
    @property
    def base_url(self) -> str:
        return f"{Config.get('server')}{Config.get('apiVersion')}"

    @property
    def timeout(self) -> float:
        return float(Config.get("REQUEST_TIMEOUT", 10))

    def _send(self, method: str, path_suffix: str = "", json: Any = None) -> requests.Response:
        response = requests.request(
            method=method,
            url=f"{self.base_url}{self.endpoint.value.url}{path_suffix}",
            headers=self.request_spec,
            json=json,
            timeout=self.timeout
        )
        self.response_spec(response)
        return response
    
    def post(self, model: T | None = None) -> requests.Response:
        body = model.model_dump() if model is not None else None
        return self._send("POST", json=body)

    def get(self, id: int | None = None): 
        path_suffix = f"/{id}" if id is not None else ""
        return self._send("GET", path_suffix=path_suffix)

    def update(self, model: BaseModel, id: int | None = None) -> requests.Response:
        body = model.model_dump() if model is not None else ''

        response = requests.put(
            url=f'{self.base_url}{self.endpoint.value.url}{("/" + str(id)) if id is not None else ""}',
            headers=self.request_spec,
            json=body
        )
        self.response_spec(response)
        return response

    def delete(self, id: int) -> requests.Response:
        response = requests.delete(
            url=f'{self.base_url}{self.endpoint.value.url}/{id}',
            headers=self.request_spec
        )
        self.response_spec(response)
        return response
