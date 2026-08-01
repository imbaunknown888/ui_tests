from src.main.ui.elements.base_element import BaseElement


class UserBadge(BaseElement):
    @property
    def _lines(self):
        text = self.element.inner_text()
        return text.splitlines()

    @property
    def _text(self) -> str:
        return self.element.inner_text().strip()

    @property
    def username(self) -> str:
        if self._lines:
            line = self._lines[0]
            if line.endswith("ADMIN"):
                return line[:-5]
            if line.endswith("USER"):
                return line[:-4]
            return line
        return ""

    @property
    def role(self) -> str:
        if len(self._lines) > 1:
            return self._lines[1]
        if self._text.endswith("ADMIN"):
            return "ADMIN"
        if self._text.endswith("USER"):
            return "USER"
        return ""
