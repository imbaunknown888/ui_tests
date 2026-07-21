from http import HTTPStatus
from enum import Enum
from typing import Callable
from requests import Response


class ResponseSpecs:
    @staticmethod
    def _make_status_checker(expected_statuses: list[HTTPStatus]) -> Callable[[Response], None]:
        def check(response: Response):
            assert response.status_code in expected_statuses, (
                f"Expected status {expected_statuses}, but got {response.status_code}. "
                f"Response body: {response.text}"
            )
        return check

    @staticmethod
    def request_returns_ok() -> Callable[[Response], None]:
        return ResponseSpecs._make_status_checker([HTTPStatus.OK])

    @staticmethod
    def entity_was_created() -> Callable[[Response], None]:
        return ResponseSpecs._make_status_checker([HTTPStatus.CREATED])

    @staticmethod
    def entity_was_deleted() -> Callable[[Response], None]:
        return ResponseSpecs._make_status_checker([HTTPStatus.OK, HTTPStatus.NO_CONTENT])

    @staticmethod
    def request_returns_bad_request(
        error_key: str,
        error_value: str | Enum | list[str | Enum]
    ) -> Callable[[Response], None]:
        def check(response: Response):
            assert response.status_code == HTTPStatus.BAD_REQUEST, (
                f"Expected 400 BAD_REQUEST, got {response.status_code}. Response: {response.text}"
            )
            actual_value = response.json().get(error_key)
            expected_values = error_value if isinstance(error_value, list) else [error_value]
            expected_values = [
                str(value.value if isinstance(value, Enum) else value)
                for value in expected_values
            ]
            actual_values = actual_value if isinstance(actual_value, list) else [actual_value]
            actual_values = [str(value) for value in actual_values]
            assert any(expected in actual for expected in expected_values for actual in actual_values), (
                f"Expected error field '{error_key}' to contain one of {expected_values}, but got {actual_values}."
            )
        return check
