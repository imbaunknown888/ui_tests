import pytest
from playwright.sync_api import Page, expect

from src.main.ui.pages.login_page import LoginPage
from src.main.ui.pages.admin_panel import AdminPanel
from src.main.ui.pages.user_dashboard import UserDashboard
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.mark.ui
@pytest.mark.browsers("webkit")
class TestLoginUser:
    def test_admin_can_login_with_correct_data(self, page: Page, api_manager: ApiManager, admin_user_request: CreateUserRequest):
        login_page = LoginPage(page).open()
        login_page.login(admin_user_request.username, admin_user_request.password)
        admin_page = login_page.get_page(AdminPanel)
        expect(admin_page.admin_panel_text).to_be_visible()

        user_dao = api_manager.database_steps.get_user_by_username(admin_user_request.username)
        assert user_dao.username == admin_user_request.username

    def test_user_can_login_with_correct_data(self, page: Page, api_manager: ApiManager, user_request: CreateUserRequest):
        login_page = LoginPage(page).open()
        login_page.login(user_request.username, user_request.password)
        user_dashboard = login_page.get_page(UserDashboard)
        expect(user_dashboard.welcome_text).to_be_visible()

        user_dao = api_manager.database_steps.get_user_by_username(user_request.username)
        assert user_dao.username == user_request.username
