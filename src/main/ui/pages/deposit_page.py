import re

from playwright.sync_api import expect

from src.main.ui.pages.base_page import BasePage


class DepositPage(BasePage):
    @property
    def title(self):
        return self.page.get_by_text("Deposit Money")

    @property
    def account_selector(self):
        return self.page.locator(".account-selector")

    @property
    def amount_input(self):
        return self.page.locator(".deposit-input")

    @property
    def deposit_button(self):
        return self.page.get_by_role("button", name=re.compile("Deposit"))

    def url(self):
        return "/deposit"

    def deposit_to_account(self, account_id: int, amount: float):
        self.wait_until_visible(self.account_selector)
        self.wait_until_enabled(self.account_selector)
        self.account_selector.locator(f"option[value='{account_id}']").wait_for(state="attached")
        self.account_selector.select_option(str(account_id))
        expect(self.account_selector).to_have_value(str(account_id))
        self.fill_text(self.amount_input, str(amount))
        with self.page.expect_response(
            lambda response: (
                "/api/v1/accounts/deposit" in response.url
                and response.request.method == "POST"
            )
        ):
            self.click_element(self.deposit_button)
        return self

    def check_page_is_visible(self):
        expect(self.title).to_be_visible()
        expect(self.account_selector).to_be_visible()
        expect(self.amount_input).to_be_visible()
        return self
