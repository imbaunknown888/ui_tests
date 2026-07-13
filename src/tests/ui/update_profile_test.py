import pytest
from playwright.sync_api import Page

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.ui.pages.bank_alert import BankAlert
from src.main.ui.pages.profile_page import ProfilePage


@pytest.mark.ui
@pytest.mark.usefixtures("browser_match_guard")
@pytest.mark.prepare_users(number=1)
class TestUpdateProfile:
    def test_user_can_update_profile_name(
        self,
        api_manager: ApiManager,
        page: Page,
        prepared_users: list[CreateUserRequest],
    ):
        user = prepared_users[0]
        new_name = RandomData.get_profile_name()

        ProfilePage(page).auth_as_user(user)
        ProfilePage(page).open() \
        .check_page_is_visible() \
        .check_alert_message_and_accept(BankAlert.PROFILE_UPDATED) \
        .update_name(new_name)

        profile = api_manager.user_steps.get_profile(user)
        assert profile.name == new_name
