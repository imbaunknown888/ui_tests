from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from time import monotonic, sleep
from typing import TypeVar

from playwright.sync_api import Dialog, Locator, Page, expect
from typing_extensions import Self

from src.main.api.configs.config import Config
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.specs.request_specs import RequestSpecs

T = TypeVar("T", bound="BasePage")

class BasePage(ABC):
    def __init__(self, page: Page):
        self.page = page
        self.base_url = str(Config.get("UI_BASE_URL", "http://localhost:3000")).rstrip("/")

    @property
    def username_input(self):
        return self.page.get_by_placeholder("Username")
        
    @property
    def password_input(self):
        return self.page.get_by_placeholder("Password")

    @abstractmethod
    def url(self) -> str:
        raise NotImplementedError

    def open(self) -> Self:
        target = self.url()
        if self.base_url and target.startswith("/"):
            target = f"{self.base_url}{target}"
        self.page.goto(target, wait_until="domcontentloaded")
        return self

    def get_page(self, page_cls: type[T]) -> T:
        return page_cls(self.page)

    def wait_until_visible(self, locator: Locator) -> Locator:
        expect(locator).to_be_visible()
        return locator

    def wait_until_enabled(self, locator: Locator) -> Locator:
        expect(locator).to_be_enabled()
        return locator

    def fill_text(self, locator: Locator, value: str) -> None:
        self.wait_until_visible(locator)
        self.wait_until_enabled(locator)
        locator.fill(value)
        expect(locator).to_have_value(value)

    def click_element(self, locator: Locator) -> None:
        self.wait_until_visible(locator)
        self.wait_until_enabled(locator)
        locator.click()

    def retry_until(
        self,
        condition: Callable[[], bool],
        message: str,
        timeout: float = 5.0,
        interval: float = 0.2,
    ) -> None:
        deadline = monotonic() + timeout
        while monotonic() < deadline:
            if condition():
                return
            sleep(interval)
        assert condition(), message

    def check_alert_message_and_accept(self, expected_text: str) -> Self:
        messages: list[str] = []

        def _handler(d: Dialog) -> None:
            messages.append(d.message)
            try:
                d.accept()
            finally:
                assert expected_text in messages[-1], f"Alert text mismatch: {messages[-1]}"

        self.page.once("dialog", _handler)
        return self
    
    def auth_as_user(self, user_request: CreateUserRequest) -> None:
        auth_token = RequestSpecs.auth_as_user(user_request.username, user_request.password).get("Authorization")
        self.page.set_viewport_size({"width": 1920, "height": 1080})
        self.page.goto(self.base_url)
        self.page.evaluate('token => localStorage.setItem("authToken", token)', auth_token)

    def _generate_page_elements(self, elements: Locator, constructor: Callable[[Locator], T]) -> list[T]:
        count = elements.count()
        if count == 0:
            return []
        expect(elements.first).to_be_visible()
        return [constructor(elements.nth(i)) for i in range(elements.count())]
