import pytest
from playwright.sync_api import Page

from src.main.api.fixtures.prepare_data_fixtures import PreparedUserAccount
from src.main.api.generators.random_data import RandomData
from src.main.ui.pages.bank_alert import BankAlert
from src.main.ui.pages.deposit_page import DepositPage


@pytest.mark.ui
@pytest.mark.usefixtures("browser_match_guard")
@pytest.mark.prepare_users(number=1)
@pytest.mark.prepare_accounts(number=1)
class TestDepositAccount:
    @pytest.fixture()
    def deposit_amount(self) -> float:
        return RandomData.get_amount()

    @pytest.mark.check_account_balance_change(
        user_source="prepared_user_accounts.0.user",
        account_id_source="prepared_user_accounts.0.account.id",
        delta_source="deposit_amount",
        expected_balance_source="deposit_amount",
    )
    def test_user_can_deposit_to_account(
        self,
        page: Page,
        prepared_user_accounts: list[PreparedUserAccount],
        deposit_amount: float,
    ):
        prepared_user_account = prepared_user_accounts[0]

        DepositPage(page).auth_as_user(prepared_user_account.user)
        DepositPage(page).open() \
            .check_page_is_visible() \
            .check_alert_message_and_accept(BankAlert.DEPOSIT_SUCCESSFUL) \
            .deposit_to_account(prepared_user_account.account.id, deposit_amount)
