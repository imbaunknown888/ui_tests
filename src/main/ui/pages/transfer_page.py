import re

from playwright.sync_api import expect

from src.main.ui.pages.base_page import BasePage


class TransferPage(BasePage):
    @property
    def title(self):
        return self.page.get_by_text("Make a Transfer")

    @property
    def account_selector(self):
        return self.page.locator(".account-selector")

    @property
    def recipient_account_input(self):
        return self.page.get_by_placeholder("Enter recipient account number")

    @property
    def recipient_name_input(self):
        return self.page.get_by_placeholder("Enter recipient name")

    @property
    def amount_input(self):
        return self.page.locator("input[placeholder='Enter amount']").first

    @property
    def confirm_checkbox(self):
        return self.page.locator("#confirmCheck")

    @property
    def send_transfer_button(self):
        return self.page.get_by_role("button", name=re.compile("Send Transfer"))

    def url(self):
        return "/transfer"

    def transfer_to_account(self, sender_account_id: int, receiver_name: str, receiver_account_number: str, amount: float):
        self.wait_until_visible(self.account_selector)
        self.wait_until_enabled(self.account_selector)
        self.account_selector.locator(f"option[value='{sender_account_id}']").wait_for(state="attached")
        self.account_selector.select_option(str(sender_account_id))
        expect(self.account_selector).to_have_value(str(sender_account_id))
        self.fill_text(self.recipient_name_input, receiver_name)
        self.fill_text(self.recipient_account_input, receiver_account_number)
        self.fill_text(self.amount_input, str(amount))
        self.wait_until_visible(self.confirm_checkbox)
        self.confirm_checkbox.check()
        expect(self.confirm_checkbox).to_be_checked()
        with self.page.expect_response(lambda response: "/api/v1/accounts/transfer" in response.url):
            self.click_element(self.send_transfer_button)
        return self

    def check_page_is_visible(self):
        expect(self.title).to_be_visible()
        expect(self.account_selector).to_be_visible()
        expect(self.recipient_account_input).to_be_visible()
        expect(self.recipient_name_input).to_be_visible()
        expect(self.amount_input).to_be_visible()
        return self
