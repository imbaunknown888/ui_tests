from typing import List

from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.requests.steps.base_steps import BaseSteps
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.models.login_user_request import LoginUserRequest
from src.main.api.models.login_user_response import LoginUserResponse
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.comparison.model_assertions import models_match
from src.main.api.models.user_profile_response import UserProfileResponse
from src.main.api.models.create_account_response import CreateAccountResponse
from src.main.api.models.deposit_request import DepositRequest
from src.main.api.models.deposit_response import DepositResponse
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.models.transfer_response import TransferResponse
from src.main.api.models.update_profile_request import UpdateProfileRequest
from src.main.api.requests.skeleton.requesters.validated_crud_requester import ValidatedCrudRequester


class UserSteps(BaseSteps):
    def login(self, user_request: CreateUserRequest) -> LoginUserResponse:
        login_request = LoginUserRequest(username=user_request.username, password=user_request.password)
        login_response: LoginUserResponse = ValidatedCrudRequester(
            RequestSpecs.unauth_spec(),
            Endpoint.LOGIN_USER,
            ResponseSpecs.request_returns_ok()
        ).post(login_request)
        models_match(login_request, login_response)
        return login_response

    def create_account(self, user_request: CreateUserRequest) -> CreateAccountResponse:
        create_account_response: CreateAccountResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.CREATE_ACCOUNT,
            ResponseSpecs.entity_was_created()
        ).post()

        return create_account_response
    
    def get_all_accounts(self, user_request: CreateUserRequest) -> List[CreateAccountResponse]:
        user_accounts: List[CreateAccountResponse] = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.GET_CUSTOMER_ACCOUNTS,
            ResponseSpecs.request_returns_ok()
        ).get()

        return user_accounts
    
    def get_profile(self, user_request: CreateUserRequest):
        user_profile: UserProfileResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.GET_CUSTOMER_PROFILE,
            ResponseSpecs.request_returns_ok()
        ).get()

        return user_profile

    def deposit_to_account(self, user_request: CreateUserRequest, account_id: int, amount: float) -> DepositResponse:
        account = next(
            account for account in self.get_all_accounts(user_request)
            if account.id == account_id
        )
        deposit_request = DepositRequest(
            id=account.id,
            accountNumber=account.accountNumber,
            balance=amount,
        )
        deposit_response: DepositResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.DEPOSIT_TO_ACCOUNT,
            ResponseSpecs.request_returns_ok()
        ).post(deposit_request)
        return deposit_response

    def update_profile(self, user_request: CreateUserRequest, name: str) -> UserProfileResponse:
        update_profile_request = UpdateProfileRequest(name=name)
        user_profile: UserProfileResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.UPDATE_CUSTOMER_PROFILE,
            ResponseSpecs.request_returns_ok()
        ).update(update_profile_request)
        return user_profile

    def transfer_to_account(
        self,
        user_request: CreateUserRequest,
        transfer_request: TransferRequest,
    ) -> TransferResponse:
        transfer_response: TransferResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.TRANSFER_TO_ACCOUNT,
            ResponseSpecs.request_returns_ok()
        ).post(transfer_request)
        return transfer_response

    def transfer_with_fraud_check(
        self,
        user_request: CreateUserRequest,
        transfer_request: TransferRequest,
    ) -> TransferResponse:
        transfer_response: TransferResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.TRANSFER_WITH_FRAUD_CHECK,
            ResponseSpecs.request_returns_ok()
        ).post(transfer_request)
        return transfer_response
