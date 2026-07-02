import pytest

from src.main.api.models.role import Role
from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.models.alert_messages import AlertMessages
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.generators.random_model_generator import RandomModelGenerator


@pytest.mark.api
class TestCreateUser:
    @pytest.mark.parametrize('create_user_request', [RandomModelGenerator.generate(CreateUserRequest)])
    def test_create_valid_user(self, api_manager: ApiManager, create_user_request: CreateUserRequest):
        api_manager.admin_steps.create_user(create_user_request)
    
    @pytest.mark.parametrize(
        'username, password, role, error_key, error_value',
        [
            ('', RandomData.get_password(), Role.USER, 'username', AlertMessages.USERNAME_CANNOT_BE_BLANK),
            (RandomData.get_username(2), RandomData.get_password(), Role.USER, 'username', AlertMessages.USERNAME_MUST_BY_BETWEEN_3_AND_5_CHARACTERS),
            (RandomData.get_username(16), RandomData.get_password(), Role.USER, 'username', AlertMessages.USERNAME_MUST_BY_BETWEEN_3_AND_5_CHARACTERS),
            (f'@{RandomData.get_username()}', RandomData.get_password(), Role.USER, 'username', AlertMessages.USERNAME_MUST_CONTAIN_ONLY_ALLOWED_SYMBOLS),
        ]
    )
    def test_create_invalid_user(self, api_manager: ApiManager, username: str, password: str, role: str, error_key: str, error_value: str):
        create_user_request = CreateUserRequest(username=username, password=password, role=role)
        api_manager.admin_steps.create_invalid_user(create_user_request, error_key, error_value)
    