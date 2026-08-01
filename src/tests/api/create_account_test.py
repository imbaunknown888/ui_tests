import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.comparison.model_assertions import DaoAndModelAssertions


@pytest.mark.api
class TestCreateAccount:
    def test_create_account(self, api_manager: ApiManager, user_request: CreateUserRequest):
        create_account_response = api_manager.user_steps.create_account(user_request)

        account_dao = api_manager.database_steps.get_account_by_account_number(
            create_account_response.accountNumber
        )
        DaoAndModelAssertions.assert_that(create_account_response, account_dao).match()
