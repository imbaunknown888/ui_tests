import pytest
from playwright.sync_api import Page

from src.main.api.classes.api_manager import ApiManager
from src.main.api.fixtures.prepare_data_fixtures import PreparedUserAccount
from src.main.api.generators.random_data import RandomData
from src.main.ui.pages.bank_alert import BankAlert
from src.main.ui.pages.transfer_page import TransferPage


@pytest.mark.ui
@pytest.mark.usefixtures("browser_match_guard")
@pytest.mark.prepare_users(number=2)
@pytest.mark.prepare_accounts(number=2)
class TestTransferAccount:
    def test_user_can_transfer_money_to_another_account(
        self,
        api_manager: ApiManager,
        page: Page,
        prepared_user_accounts: list[PreparedUserAccount],
    ):
        sender = prepared_user_accounts[0]
        receiver = prepared_user_accounts[1]
        sender_initial_balance = RandomData.get_amount(2000.0, 5000.0)
        receiver_initial_balance = RandomData.get_amount(1000.0, 1999.0)
        transfer_amount = RandomData.get_amount(1.0, sender_initial_balance)

        api_manager.user_steps.deposit_to_account(
            sender.user,
            sender.account.id,
            sender_initial_balance,
        )
        api_manager.user_steps.deposit_to_account(
            receiver.user,
            receiver.account.id,
            receiver_initial_balance,
        )

        TransferPage(page).auth_as_user(sender.user)
        TransferPage(page).open() \
        .check_page_is_visible() \
        .check_alert_message_and_accept(BankAlert.TRANSFER_SUCCESSFUL) \
        .transfer_to_account(
            sender.account.id,
            receiver.user.username,
            receiver.account.accountNumber,
            transfer_amount,
        )

        sender_accounts = api_manager.user_steps.get_all_accounts(sender.user)
        receiver_accounts = api_manager.user_steps.get_all_accounts(receiver.user)

        sender_account = next(account for account in sender_accounts if account.id == sender.account.id)
        receiver_account = next(account for account in receiver_accounts if account.id == receiver.account.id)

        assert sender_account.balance == pytest.approx(sender_initial_balance - transfer_amount)
        assert receiver_account.balance == pytest.approx(receiver_initial_balance + transfer_amount)
