import shutil
import typing
from .libs import *


@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session: pytest.Session, exitstatus: int):
    stop_playwright()


def migrate_test_resources():
    root_path = pathlib2.Path(f'tests{os.sep}res').absolute().as_posix()
    logger.debug('start migrating test-resources')
    shutil.copytree(root_path, '.')

            


migrate_test_resources()
