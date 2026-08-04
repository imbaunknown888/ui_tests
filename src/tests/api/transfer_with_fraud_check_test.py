from dataclasses import dataclass

import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.fixtures.prepare_data_fixtures import PreparedUserAccount
from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.models.transfer_response import TransferResponse


TRANSFER_AMOUNT = 123.45
INITIAL_DEPOSIT = 5000.0


@dataclass(frozen=True)
class FraudScenario:
    expected_status: str
    expected_message: str
    risk_score: float
    reason: str
    requires_manual_review: bool
    requires_verification: bool
    should_transfer_money: bool


APPROVED = FraudScenario(
    expected_status="APPROVED",
    expected_message="Transfer approved and processed immediately",
    risk_score=0.2,
    reason="Low risk transaction",
    requires_manual_review=False,
    requires_verification=False,
    should_transfer_money=True,
)

APPROVED_WITH_VERIFICATION = FraudScenario(
    expected_status="APPROVED",
    expected_message="Transfer approved and processed immediately",
    risk_score=0.45,
    reason="Additional verification required",
    requires_manual_review=False,
    requires_verification=True,
    should_transfer_money=True,
)

REJECTED = FraudScenario(
    expected_status="MANUAL_REVIEW_REQUIRED",
    expected_message="Transfer requires manual review",
    risk_score=0.95,
    reason="High risk transaction",
    requires_manual_review=False,
    requires_verification=False,
    should_transfer_money=False,
)

MANUAL_REVIEW = FraudScenario(
    expected_status="MANUAL_REVIEW_REQUIRED",
    expected_message="Transfer requires manual review",
    risk_score=0.7,
    reason="Manual review required",
    requires_manual_review=True,
    requires_verification=False,
    should_transfer_money=False,
)


def _account_by_id(
    api_manager: ApiManager,
    user: CreateUserRequest,
    account_id: int,
) -> CreateAccountResponse:
    return next(
        account
        for account in api_manager.user_steps.get_all_accounts(user)
        if account.id == account_id
    )


@pytest.mark.api
@pytest.mark.api_version("with_fraud_check_with_transfer_fix")
@pytest.mark.prepare_users(number=2)
@pytest.mark.prepare_accounts(number=2, deposit=INITIAL_DEPOSIT)
class TestTransferWithFraudCheck:
    @pytest.mark.parametrize(
        "scenario",
        [
            pytest.param(
                APPROVED,
                marks=pytest.mark.fraud_check_mock(
                    port=8080,
                    endpoint=r"/.*",
                    status="SUCCESS",
                    decision="APPROVED",
                    riskScore=APPROVED.risk_score,
                    reason=APPROVED.reason,
                    requiresManualReview=APPROVED.requires_manual_review,
                    additionalVerificationRequired=APPROVED.requires_verification,
                ),
                id="approved",
            ),
            pytest.param(
                APPROVED_WITH_VERIFICATION,
                marks=pytest.mark.fraud_check_mock(
                    port=8080,
                    endpoint=r"/.*",
                    status="SUCCESS",
                    decision="APPROVED",
                    riskScore=APPROVED_WITH_VERIFICATION.risk_score,
                    reason=APPROVED_WITH_VERIFICATION.reason,
                    requiresManualReview=APPROVED_WITH_VERIFICATION.requires_manual_review,
                    additionalVerificationRequired=APPROVED_WITH_VERIFICATION.requires_verification,
                ),
                id="approved-with-verification",
            ),
            pytest.param(
                REJECTED,
                marks=pytest.mark.fraud_check_mock(
                    port=8080,
                    endpoint=r"/.*",
                    status="SUCCESS",
                    decision="REJECTED",
                    riskScore=REJECTED.risk_score,
                    reason=REJECTED.reason,
                    requiresManualReview=REJECTED.requires_manual_review,
                    additionalVerificationRequired=REJECTED.requires_verification,
                ),
                id="rejected",
            ),
            pytest.param(
                MANUAL_REVIEW,
                marks=pytest.mark.fraud_check_mock(
                    port=8080,
                    endpoint=r"/.*",
                    status="SUCCESS",
                    decision="MANUAL_REVIEW",
                    riskScore=MANUAL_REVIEW.risk_score,
                    reason=MANUAL_REVIEW.reason,
                    requiresManualReview=MANUAL_REVIEW.requires_manual_review,
                    additionalVerificationRequired=MANUAL_REVIEW.requires_verification,
                ),
                id="manual-review",
            ),
        ],
    )
    def test_transfer_with_fraud_check_uses_mocked_decision(
        self,
        api_manager: ApiManager,
        prepared_user_accounts: list[PreparedUserAccount],
        scenario: FraudScenario,
    ):
        with allure.step("Prepare sender and receiver accounts"):
            sender = prepared_user_accounts[0]
            receiver = prepared_user_accounts[1]
            sender_before = _account_by_id(api_manager, sender.user, sender.account.id)
            receiver_before = _account_by_id(api_manager, receiver.user, receiver.account.id)

        with allure.step("Transfer with fraud check"):
            transfer_request = TransferRequest(
                senderAccountId=sender.account.id,
                receiverAccountId=receiver.account.id,
                amount=TRANSFER_AMOUNT,
            )
            transfer_response = api_manager.user_steps.transfer_with_fraud_check(
                sender.user,
                transfer_request,
            )

        with allure.step("Validate transfer response matches mocked fraud decision"):
            expected = TransferResponse(
                status=scenario.expected_status,
                message=scenario.expected_message,
                amount=TRANSFER_AMOUNT,
                senderAccountId=sender.account.id,
                receiverAccountId=receiver.account.id,
                fraudRiskScore=scenario.risk_score,
                fraudReason=scenario.reason,
                requiresManualReview=scenario.requires_manual_review,
                requiresVerification=scenario.requires_verification,
            )
            ModelAssertions(expected, transfer_response).match()

        with allure.step("Validate account balances after fraud decision"):
            sender_after = _account_by_id(api_manager, sender.user, sender.account.id)
            receiver_after = _account_by_id(api_manager, receiver.user, receiver.account.id)

            if scenario.should_transfer_money:
                assert sender_after.balance == pytest.approx(sender_before.balance - TRANSFER_AMOUNT)
                assert receiver_after.balance == pytest.approx(receiver_before.balance + TRANSFER_AMOUNT)
            else:
                assert sender_after.balance == pytest.approx(sender_before.balance)
                assert receiver_after.balance == pytest.approx(receiver_before.balance)
