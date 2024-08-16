import os
import shutil
import pytest
from unittest.mock import patch, MagicMock
import bot

@pytest.fixture(scope="module")
def temp_config_file(tmpdir_factory):
    temp_dir = tmpdir_factory.mktemp("config")
    temp_config_path = os.path.join(temp_dir, "src/tools/config/config.yml")

    os.makedirs(os.path.dirname(temp_config_path), exist_ok=True)

    example_config_path = "src/tools/config/_config.yml"
    shutil.copy(example_config_path, temp_config_path)

    bot.config_path = temp_config_path

    yield temp_config_path

    shutil.rmtree(temp_dir)

def test_config_file_exists(temp_config_file):
    assert os.path.exists(temp_config_file), "配置文件不存在"

def test_ensure_folder_exists():
    test_path = "test_folder"
    
    if os.path.isdir(test_path):
        os.rmdir(test_path)

    assert not os.path.isdir(test_path), "测试文件夹已存在"

    bot.ensure_folder_exists(test_path)
    assert os.path.isdir(test_path), "测试文件夹未被创建"

    os.rmdir(test_path)

def test_ensure_folders_exist():
    test_structure = {
        "test_src": {
            "test_data": None,
            "test_cache": None
        }
    }

    if os.path.isdir("test_src"):
        for root, dirs, files in os.walk("test_src", topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir("test_src")

    assert not os.path.isdir("test_src"), "测试文件夹结构已存在"

    bot.ensure_folders_exist(test_structure)
    assert os.path.isdir("test_src"), "根文件夹未被创建"
    assert os.path.isdir("test_src/test_data"), "子文件夹未被创建"
    assert os.path.isdir("test_src/test_cache"), "子文件夹未被创建"

    for root, dirs, files in os.walk("test_src", topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir("test_src")

@patch("nonebot.init", MagicMock())
def test_nonebot_initialization():
    bot.nonebot.init()
    assert bot.nonebot.init.called, "Nonebot 初始化未被调用"
