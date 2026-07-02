import pytest
from playwright.sync_api import Page

from src.main.api.classes.api_manager import ApiManager
from src.main.api.fixtures.prepare_data_fixtures import PreparedUserAccount
from src.main.api.generators.random_data import RandomData
from src.main.ui.pages.bank_alert import BankAlert
from src.main.ui.pages.deposit_page import DepositPage


@pytest.mark.ui
@pytest.mark.usefixtures("browser_match_guard")
@pytest.mark.prepare_users(number=1)
@pytest.mark.prepare_accounts(number=1)
class TestDepositAccount:
    def test_user_can_deposit_to_account(
        self,
        api_manager: ApiManager,
        page: Page,
        prepared_user_accounts: list[PreparedUserAccount],
    ):
        prepared_user_account = prepared_user_accounts[0]
        deposit_amount = RandomData.get_amount()

        DepositPage(page).auth_as_user(prepared_user_account.user)
        DepositPage(page).open() \
        .check_page_is_visible() \
        .check_alert_message_and_accept(BankAlert.DEPOSIT_SUCCESSFUL) \
        .deposit_to_account(prepared_user_account.account.id, deposit_amount)

        accounts = api_manager.user_steps.get_all_accounts(prepared_user_account.user)
        updated_account = next(
            account for account in accounts
            if account.id == prepared_user_account.account.id
        )
        assert updated_account.balance == deposit_amount
