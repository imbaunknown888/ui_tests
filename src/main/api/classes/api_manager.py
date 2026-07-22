from src.main.api.requests.steps.admin_steps import AdminSteps
from src.main.api.requests.steps.user_steps import UserSteps
from src.main.api.requests.steps.database_steps import DataBaseSteps


class ApiManager:
    def __init__(self, created_objects: list):
        self.admin_steps = AdminSteps(created_objects)
        self.user_steps = UserSteps(created_objects)
        self.database_steps = DataBaseSteps