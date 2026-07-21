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