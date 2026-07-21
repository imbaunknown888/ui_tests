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
    @pytest.fixture()
    def sender_initial_balance(self) -> float:
        return RandomData.get_amount(2000.0, 5000.0)

    @pytest.fixture()
    def receiver_initial_balance(self) -> float:
        return RandomData.get_amount(1000.0, 1999.0)

    @pytest.fixture()
    def transfer_amount(self, sender_initial_balance: float) -> float:
        return RandomData.get_amount(1.0, sender_initial_balance)

    @pytest.fixture()
    def funded_transfer_accounts(
        self,
        api_manager: ApiManager,
        prepared_user_accounts: list[PreparedUserAccount],
        sender_initial_balance: float,
        receiver_initial_balance: float,
    ) -> list[PreparedUserAccount]:
        sender = prepared_user_accounts[0]
        receiver = prepared_user_accounts[1]

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
        return prepared_user_accounts

    @pytest.mark.check_account_balance_change(
        user_source="funded_transfer_accounts.0.user",
        account_id_source="funded_transfer_accounts.0.account.id",
        delta_source="transfer_amount",
        direction=-1,
    )
    @pytest.mark.check_account_balance_change(
        user_source="funded_transfer_accounts.1.user",
        account_id_source="funded_transfer_accounts.1.account.id",
        delta_source="transfer_amount",
    )
    def test_user_can_transfer_money_to_another_account(
        self,
        page: Page,
        funded_transfer_accounts: list[PreparedUserAccount],
        transfer_amount: float,
    ):
        sender = funded_transfer_accounts[0]
        receiver = funded_transfer_accounts[1]

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
