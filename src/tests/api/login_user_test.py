import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.mark.api
class TestLoginUser:
    def test_login_user(self, api_manager: ApiManager, user_request: CreateUserRequest):
        login_response = api_manager.user_steps.login(user_request)

        user_dao = api_manager.database_steps.get_user_by_username(login_response.username)
        assert user_dao.username == login_response.username

    def test_login_admin_user(self, api_manager: ApiManager, admin_user_request: CreateUserRequest):
        login_response = api_manager.user_steps.login(admin_user_request)

        user_dao = api_manager.database_steps.get_user_by_username(login_response.username)
        assert user_dao.username == login_response.username
