from enum import Enum


class AlertMessages(str, Enum):
    USERNAME_CANNOT_BE_BLANK = "Username cannot be blank"
    USERNAME_MUST_BY_BETWEEN_3_AND_5_CHARACTERS = "Username must be between 3 and 15 characters"
    USERNAME_MUST_CONTAIN_ONLY_ALLOWED_SYMBOLS = "Username must contain only letters, digits, dashes, underscores, and dots"
