import shutil
import typing
from .libs import *


@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session: pytest.Session, exitstatus: int):
    stop_playwright()


def migrate_test_resources():
    root_path = f'tests{os.sep}res'
    r_len = len(root_path)
    for root, dirs, files in os.walk(root_path):
        if not files:
            continue
        logger.debug(f'testingenv migrate:{files}')
        for file in files:
            shutil.copy(f'{root}{os.sep}{file}', f'{root[r_len+1:]}{os.sep}{file}')


migrate_test_resources()
