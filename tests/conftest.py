import shutil
import typing
from .libs import *


@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session: pytest.Session, exitstatus: int):
    stop_playwright()


def migrate_test_resources():
    current = pathlib2.Path(__file__).parent.parent.parent  # file->res->tests
    root_path = pathlib2.Path(f'tests{os.sep}res').absolute().as_posix()
    r_len = len(root_path)
    logger.debug('start migrating test-resources')

    for root, dirs, files in os.walk(root_path):
        if not files:
            continue
        if not os.path.exists(root):
            os.makedirs(root)

        for file in files:
            source = f'{root}{os.sep}{file}'
            target = f'{current}{os.sep}{root[r_len:]}{os.sep}{file}'
            logger.debug(f'testingenv migrate:{source} to {target}')
            shutil.copy(source, target)


migrate_test_resources()
