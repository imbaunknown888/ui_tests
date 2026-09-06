from collections.abc import Callable, Iterable
from http import HTTPStatus

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
        error_value: str | Iterable[str]
    ) -> Callable[[Response], None]:
        def check(response: Response):
            assert response.status_code == HTTPStatus.BAD_REQUEST, (
                f"Expected 400 BAD_REQUEST, got {response.status_code}. Response: {response.text}"
            )

            expected_errors = ResponseSpecs._to_error_list(error_value)
            actual_value = response.json().get(error_key)
            actual_errors = ResponseSpecs._to_error_list(actual_value)

            missing_errors = [
                expected
                for expected in expected_errors
                if not any(expected in actual for actual in actual_errors)
            ]
            assert not missing_errors, (
                f"Expected error field '{error_key}' to contain {expected_errors}, "
                f"but got {actual_errors}. Missing: {missing_errors}."
            )
        return check

    @staticmethod
    def _to_error_list(value) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, dict):
            return ResponseSpecs._to_error_list(value.values())
        if isinstance(value, Iterable):
            result: list[str] = []
            for item in value:
                result.extend(ResponseSpecs._to_error_list(item))
            return result
        return [str(value)]
