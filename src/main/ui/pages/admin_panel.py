
from playwright.sync_api import Locator, expect

from src.main.ui.elements.user_badge import UserBadge
from src.main.ui.pages.base_page import BasePage


class AdminPanel(BasePage):
    @property
    def admin_panel_text(self):
        return self.page.get_by_text("Admin Panel")
    
    @property
    def add_user_button(self):
        return self.page.get_by_role("button", name="Add User")
    
    def url(self):
        return "/admin"
    
    def create_user(self, username: str, password: str, wait_for_users_refresh: bool = False):
        self.fill_text(self.username_input, username)
        self.fill_text(self.password_input, password)

        def is_create_user_response(response):
            return (
                "/api/v1/admin/users" in response.url
                and response.request.method == "POST"
            )

        def is_get_users_response(response):
            return (
                "/api/v1/admin/users" in response.url
                and response.request.method == "GET"
            )

        if wait_for_users_refresh:
            with (
                self.page.expect_response(is_get_users_response),
                self.page.expect_response(is_create_user_response),
            ):
                self.click_element(self.add_user_button)
        else:
            with self.page.expect_response(is_create_user_response):
                self.click_element(self.add_user_button)
        return self
    
    def get_all_users_container_locator(self) -> Locator:
        return self.page.locator(".card.shadow-custom:has(:has-text('All Users'))")

    def get_all_users_locator(self) -> Locator:
        return self.get_all_users_container_locator().locator("li.list-group-item")

    def get_user_locator(self, username: str) -> Locator:
        return self.get_all_users_container_locator().get_by_text(username, exact=True)
    
    def get_all_users(self) -> list[UserBadge]:
        return self._generate_page_elements(self.get_all_users_locator(), UserBadge)
    
    def wait_for_username(self, username: str):
        self.retry_until(
            lambda: any(user.username == username for user in self.get_all_users()),
            f"User '{username}' was not found in users list.",
        )
        return self

    def check_page_is_visible(self):
        expect(self.admin_panel_text).to_be_visible()
        expect(self.add_user_button).to_be_visible()
        return self

    def check_user_is_visible(self, username: str):
        self.retry_until(
            lambda: not any(user.username == username for user in self.get_all_users()),
            f"User '{username}' should not be present in users list.",
        )
        return self
