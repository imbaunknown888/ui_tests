from typing import Optional

from src.main.api.database.db_client import Condition, DBRequest, RequestType
from src.main.api.models.dao.account_dao import AccountDao
from src.main.api.models.dao.user_dao import UserDao


class DataBaseSteps:
    @staticmethod
    def get_user_by_username(username: str) -> UserDao:
        return (
            DBRequest.builder()
            .request_type(RequestType.SELECT)
            .table("customers")
            .where(Condition.equal_to("username", username))
            .extract_as(UserDao)
        )

    @staticmethod
    def find_user_by_username(username: str) -> Optional[UserDao]:
        return (
            DBRequest.builder()
            .request_type(RequestType.SELECT)
            .table("customers")
            .where(Condition.equal_to("username", username))
            .extract_optional_as(UserDao)
        )

    @staticmethod
    def get_account_by_account_number(account_number: str) -> AccountDao:
        return (
            DBRequest.builder()
            .request_type(RequestType.SELECT)
            .table("accounts")
            .where(Condition.equal_to("account_number", account_number))
            .extract_as(AccountDao)
        )

    @staticmethod
    def find_account_by_account_number(account_number: str) -> Optional[AccountDao]:
        return (
            DBRequest.builder()
            .request_type(RequestType.SELECT)
            .table("accounts")
            .where(Condition.equal_to("account_number", account_number))
            .extract_optional_as(AccountDao)
        )
