import re

from src.main.ui.pages.base_page import BasePage
from playwright.sync_api import expect

class UserDashboard(BasePage):
    @property
    def welcome_text(self):
        return self.page.get_by_text("User Dashboard")
    
    @property
    def create_new_account_button(self):
        return self.page.get_by_role("button", name=re.compile("Create New Account"))
    
    def url(self):
        return "/dashboard"
    
    def create_new_account(self):
        with self.page.expect_response(
            lambda response: (
                "/api/v1/accounts" in response.url
                and response.request.method == "POST"
            )
        ):
            self.click_element(self.create_new_account_button)
        return self

    def check_page_is_visible(self):
        expect(self.welcome_text).to_be_visible()
        expect(self.create_new_account_button).to_be_visible()
        return self
