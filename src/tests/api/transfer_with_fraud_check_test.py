from dataclasses import dataclass
from enum import Enum

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


class FraudMockStatus(str, Enum):
    SUCCESS = "SUCCESS"


class FraudDecision(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class TransferStatus(str, Enum):
    APPROVED = "APPROVED"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"


class TransferMessage(str, Enum):
    APPROVED = "Transfer approved and processed immediately"
    MANUAL_REVIEW_REQUIRED = "Transfer requires manual review"


class FraudReason(str, Enum):
    LOW_RISK_TRANSACTION = "Low risk transaction"
    ADDITIONAL_VERIFICATION_REQUIRED = "Additional verification required"
    HIGH_RISK_TRANSACTION = "High risk transaction"
    MANUAL_REVIEW_REQUIRED = "Manual review required"


@dataclass(frozen=True)
class FraudScenario:
    decision: FraudDecision
    expected_status: TransferStatus
    expected_message: TransferMessage
    risk_score: float
    reason: FraudReason
    requires_manual_review: bool
    requires_verification: bool
    should_transfer_money: bool


APPROVED = FraudScenario(
    decision=FraudDecision.APPROVED,
    expected_status=TransferStatus.APPROVED,
    expected_message=TransferMessage.APPROVED,
    risk_score=0.2,
    reason=FraudReason.LOW_RISK_TRANSACTION,
    requires_manual_review=False,
    requires_verification=False,
    should_transfer_money=True,
)

APPROVED_WITH_VERIFICATION = FraudScenario(
    decision=FraudDecision.APPROVED,
    expected_status=TransferStatus.APPROVED,
    expected_message=TransferMessage.APPROVED,
    risk_score=0.45,
    reason=FraudReason.ADDITIONAL_VERIFICATION_REQUIRED,
    requires_manual_review=False,
    requires_verification=True,
    should_transfer_money=True,
)

REJECTED = FraudScenario(
    decision=FraudDecision.REJECTED,
    expected_status=TransferStatus.MANUAL_REVIEW_REQUIRED,
    expected_message=TransferMessage.MANUAL_REVIEW_REQUIRED,
    risk_score=0.95,
    reason=FraudReason.HIGH_RISK_TRANSACTION,
    requires_manual_review=False,
    requires_verification=False,
    should_transfer_money=False,
)

MANUAL_REVIEW = FraudScenario(
    decision=FraudDecision.MANUAL_REVIEW,
    expected_status=TransferStatus.MANUAL_REVIEW_REQUIRED,
    expected_message=TransferMessage.MANUAL_REVIEW_REQUIRED,
    risk_score=0.7,
    reason=FraudReason.MANUAL_REVIEW_REQUIRED,
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


def _fraud_scenario_param(scenario: FraudScenario, scenario_id: str):
    return pytest.param(
        scenario,
        marks=pytest.mark.fraud_check_mock(
            port=8080,
            endpoint=r"/.*",
            status=FraudMockStatus.SUCCESS.value,
            decision=scenario.decision.value,
            riskScore=scenario.risk_score,
            reason=scenario.reason.value,
            requiresManualReview=scenario.requires_manual_review,
            additionalVerificationRequired=scenario.requires_verification,
        ),
        id=scenario_id,
    )


@pytest.mark.api
@pytest.mark.api_version("with_fraud_check_with_transfer_fix")
@pytest.mark.prepare_users(number=2)
@pytest.mark.prepare_accounts(number=2, deposit=INITIAL_DEPOSIT)
class TestTransferWithFraudCheck:
    @pytest.mark.parametrize(
        "scenario",
        [
            _fraud_scenario_param(APPROVED, "approved"),
            _fraud_scenario_param(
                APPROVED_WITH_VERIFICATION,
                "approved-with-verification",
            ),
            _fraud_scenario_param(REJECTED, "rejected"),
            _fraud_scenario_param(MANUAL_REVIEW, "manual-review"),
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
                status=scenario.expected_status.value,
                message=scenario.expected_message.value,
                amount=TRANSFER_AMOUNT,
                senderAccountId=sender.account.id,
                receiverAccountId=receiver.account.id,
                fraudRiskScore=scenario.risk_score,
                fraudReason=scenario.reason.value,
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
