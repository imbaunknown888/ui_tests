import pytest

from src.main.api.utils.normalize_browsers import norm_browser_name
from src.main.api.classes.session_storage import SessionStorage
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.fixture(scope="function")
def user_session_extension(request: pytest.FixtureRequest, user_factory):
    SessionStorage.clear()
    mark = request.node.get_closest_marker("user_session")
    if not mark:
        return

    count: int = max(int(mark.args[0]), 1)
    auth_index: int = int(mark.kwargs.get("auth", 0))

    users: list[CreateUserRequest] = [user_factory() for _ in range(count)]
    SessionStorage.add_users(users)
    # UI login is needed only for UI tests. We resolve page lazily so API runs don't pull Playwright.
    page = request.getfixturevalue("page")
    from src.main.ui.pages.login_page import LoginPage

    LoginPage(page).auth_as_user(users[auth_index])


@pytest.fixture()
def admin_session_autologin(
    request: pytest.FixtureRequest, 
    admin_user_request: CreateUserRequest
):
    mark = request.node.get_closest_marker("admin_session")
    if not mark:
        return

    page = request.getfixturevalue("page")
    from src.main.ui.pages.login_page import LoginPage

    LoginPage(page).auth_as_user(admin_user_request)


@pytest.fixture()
def browser_match_guard(request):
    mark = request.node.get_closest_marker("browsers")
    if not mark:
        return

    allowed = {norm_browser_name(str(x)) for x in (mark.args or ())}
    if not allowed:
        return

    try:
        current = request.getfixturevalue("browser_name")
    except Exception:
        return

    # No runtime skip here: we filter browsers at collection-time in root conftest.py,
    # so we don't pollute reports with SKIPPED.
    return