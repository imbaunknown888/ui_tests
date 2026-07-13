from src.main.ui.pages.base_page import BasePage


class LoginPage(BasePage):
    @property
    def login_button(self):
        return self.page.get_by_role("button", name="Login")
    
    def url(self):
        return "/login"
    
    def login(self, username: str, password: str):
        self.fill_text(self.username_input, username)
        self.fill_text(self.password_input, password)
        self.click_element(self.login_button)
        return self
