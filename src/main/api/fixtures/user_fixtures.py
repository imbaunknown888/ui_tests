import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.classes.session_storage import SessionStorage
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.generators.random_model_generator import RandomModelGenerator


@pytest.fixture(scope='function')
def user_request(user_factory):
    try:
        return SessionStorage.get_user(0)
    except Exception:
        user = user_factory()
        return user


@pytest.fixture(scope="function")
def user_factory(api_manager: ApiManager):
    def create_user() -> CreateUserRequest:
        user_data = RandomModelGenerator.generate(CreateUserRequest)
        api_manager.admin_steps.create_user(user_data)
        SessionStorage.add_users([user_data])
        return user_data

    yield create_user


@pytest.fixture
def admin_user_request():
    return CreateUserRequest(username='admin', password='admin', role='ADMIN')
