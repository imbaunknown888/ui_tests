import re

from playwright.sync_api import expect

from src.main.ui.pages.base_page import BasePage


class ProfilePage(BasePage):
    @property
    def title(self):
        return self.page.get_by_text(re.compile("Profile"))

    @property
    def name_input(self):
        return self.page.locator("input[name='name'], input[placeholder*='name' i]").first

    @property
    def save_button(self):
        return self.page.get_by_role("button", name=re.compile("Save"))

    def url(self):
        return "/edit-profile"

    def update_name(self, name: str):
        self.name_input.fill(name)
        with self.page.expect_response(
            lambda response: (
                "/api/v1/customer/profile" in response.url
                and response.request.method == "PUT"
            )
        ):
            self.save_button.click()
        return self

    def check_page_is_visible(self):
        expect(self.title).to_be_visible()
        return self
