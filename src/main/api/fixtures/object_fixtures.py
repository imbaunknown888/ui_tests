from typing import Any

import pytest

from src.main.api.utils.cleanup_helper import cleanup_objects


@pytest.fixture
def created_objects():
    objects: list[Any] = []
    yield objects

    cleanup_objects(objects)