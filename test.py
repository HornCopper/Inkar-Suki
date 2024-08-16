import os
import shutil
import tempfile
import pytest
import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter

@pytest.fixture
def temp_config_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        src_config_path = 'src/tools/config/_config.yml'
        temp_config_dir = os.path.join(temp_dir, 'src/tools/config')
        os.makedirs(temp_config_dir, exist_ok=True)
        
        temp_config_path = os.path.join(temp_config_dir, 'config.yml')
        shutil.copy(src_config_path, temp_config_path)
        
        original_config_path = os.getenv("CONFIG_PATH")
        os.environ["CONFIG_PATH"] = temp_config_path
        
        yield temp_config_path
        
        if original_config_path:
            os.environ["CONFIG_PATH"] = original_config_path
        else:
            del os.environ["CONFIG_PATH"]

@pytest.mark.asyncio
async def test_nonebot_initialization(temp_config_file):
    nonebot.init()
    
    app = nonebot.get_asgi()
    
    driver = nonebot.get_driver()
    driver.register_adapter(ONEBOT_V11Adapter)
    
    nonebot.load_from_toml("pyproject.toml")
    
    assert app is not None
    assert driver is not None

    assert nonebot.get_driver().adapters
