from src.main.ui.pages.base_page import BasePage
from playwright.sync_api import expect

class UserDashboard(BasePage):
    @property
    def welcome_text(self):
        return self.page.get_by_text("User Dashboard")
    
    @property
    def create_new_account_button(self):
        return self.page.get_by_role("button", name="➕ Create New Account")
    
    def url(self):
        return "/dashboard"
    
    def create_new_account(self):
        self.create_new_account_button.click()
        return self

    def check_page_is_visible(self):
        expect(self.welcome_text).to_be_visible()
        return self