import typing
from .libs import *


@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session: pytest.Session, exitstatus: int):
    stop_playwright()

