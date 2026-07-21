import random
import uuid
from faker import Faker

faker = Faker()


class RandomData:
    @staticmethod
    def get_username(length: int | None = None) -> str:
        if length is None:
            length = random.randint(3, 15)
        return ''.join(faker.random_letters(length))

    @staticmethod
    def get_unique_username(prefix: str = "user") -> str:
        suffix = uuid.uuid4().hex[:15 - len(prefix)]
        return f"{prefix}{suffix}"
    
    @staticmethod
    def get_password() -> str:
        upper = [letter.upper() for letter in faker.random_letters(length=3)]
        lower = [letter.lower() for letter in faker.random_letters(length=3)]
        digits = [str(faker.random_digit()) for _ in range(3)]
        special = [random.choice('!@#$%^&')]
        password = upper + lower + digits + special
        random.shuffle(password)
        return ''.join(password)
