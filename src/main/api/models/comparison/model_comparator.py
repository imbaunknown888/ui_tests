from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any


@dataclass
class Mismatch:
    field_name: str
    expected: Any
    actual: Any


class ComparisonResult:
    def __init__(self, mismatches: list[Mismatch]):
        self._mismatches = mismatches

    def is_success(self) -> bool:
        return not self.mismatches
    
    @property
    def mismatches(self) -> list[Mismatch]:
        return self._mismatches 
    

class ModelComparator:
    @staticmethod
    def compare_fields(request: Any, response: Any, field_mapping: dict[str, str]):
        mismatches = []

        for request_field, response_field in field_mapping.items():
            request_value = ModelComparator._get_field_value(request, request_field)
            response_value = ModelComparator._get_field_value(response, response_field)

            if not ModelComparator._values_equal(request_value, response_value):
                mismatches.append(Mismatch(f'{request_field} -> {response_field}', request_value, response_value))
        
        return ComparisonResult(mismatches)

    @staticmethod
    def _values_equal(left: Any, right: Any) -> bool:
        if isinstance(left, bool) or isinstance(right, bool):
            return left is right

        if isinstance(left, (int, float, Decimal)) and isinstance(right, (int, float, Decimal)):
            try:
                return Decimal(str(left)) == Decimal(str(right))
            except InvalidOperation:
                return str(left) == str(right)

        return str(left) == str(right)

    def _get_field_value(obj: Any, field_name: str):
        current_class = obj.__class__

        while current_class:
            if hasattr(obj, field_name):
                return getattr(obj, field_name)
            current_class = current_class.__base__

        raise AttributeError(f'Field {field_name} not found in class {obj.__class__.__name__}')
