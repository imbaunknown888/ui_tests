import pytest
from typing import Any, List

from src.main.api.utils.cleanup_helper import cleanup_objects


@pytest.fixture
def created_objects():
    objects: List[Any] = []
    yield objects

    cleanup_objects(objects)