import logging
from typing import Any, List

from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.classes.api_manager import ApiManager


def cleanup_objects(objects: List[Any]):
    api_manager = ApiManager(objects)
    for obj in objects:
        if isinstance(obj, CreateUserResponse):
            try:
                api_manager.admin_steps.delete_user(obj.id)
            except Exception as e:
                logging.warning(f"Skip cleanup for user id '{obj.id}': {e}")
        elif isinstance(obj, CreateUserRequest):
            try:
                user_profile = api_manager.user_steps.get_profile(obj)
            except Exception as e:
                logging.warning(f"Skip cleanup for user '{getattr(obj, 'username', obj)}': {e}")
                continue
            try:
                api_manager.admin_steps.delete_user(user_profile.id)
            except Exception as e:
                logging.warning(f"Skip cleanup for user id '{user_profile.id}': {e}")
        else:
            logging.warning(f'Object type: {type(obj)} is not deleted')
