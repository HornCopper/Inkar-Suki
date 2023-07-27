from .libs import *


@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    stop_playwright()
