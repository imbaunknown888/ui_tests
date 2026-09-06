import logging
from typing import Any

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.create_user_response import CreateUserResponse

logger = logging.getLogger(__name__)


def cleanup_objects(objects: list[Any]):
    api_manager = ApiManager(objects)
    for obj in objects:
        if isinstance(obj, CreateUserResponse):
            try:
                api_manager.admin_steps.delete_user(obj.id)
            except Exception as e:  # noqa: BLE001
                logger.warning("Skip cleanup for user id '%s': %s", obj.id, e)
        elif isinstance(obj, CreateUserRequest):
            try:
                user_profile = api_manager.user_steps.get_profile(obj)
            except Exception as e:  # noqa: BLE001
                logger.warning("Skip cleanup for user '%s': %s", getattr(obj, "username", obj), e)
                continue
            try:
                api_manager.admin_steps.delete_user(user_profile.id)
            except Exception as e:  # noqa: BLE001
                logger.warning("Skip cleanup for user id '%s': %s", user_profile.id, e)
        else:
            logger.warning("Object type: %s is not deleted", type(obj))
