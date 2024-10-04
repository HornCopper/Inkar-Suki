from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext
)
from pathlib import Path
from nonebot.log import logger
from typing import Any, Dict, Literal

from src.const.path import CACHE, build_path
from src.utils.file import write
from src.utils.exceptions import BrowserNotInitializedException
from src.utils.decorators import time_record

import uuid
import asyncio

def get_uuid():
    return str(uuid.uuid1()).replace("-", "")

class ScreenshotConfig:
    """
    ScreenshotConfig defines the configuration for generating screenshots.

    Args:
        web (bool): If True, use the given path as a web URL. Defaults to False.
        locate (str): CSS selector of the element to capture. Defaults to an empty string (capture full page).
        first (bool): Capture only the first matching element if True. Defaults to False.
        delay (int): Delay (in milliseconds) before taking the screenshot. Defaults to 0.
        additional_css (str): Additional CSS to inject before taking the screenshot. Defaults to an empty string.
        additional_js (str): Additional JavaScript to execute before taking the screenshot. Defaults to an empty string.
        viewport (dict): Viewport dimensions (e.g., {"width": 1920, "height": 1080}). Defaults to 1920x1080.
        full_screen (bool): If True, capture the entire page. Defaults to False.
        hide_classes (list): List of class names for elements to hide before taking the screenshot. Defaults to an empty list.
        device_scale_factor (float): Device scale factor for higher resolution screenshots. Defaults to 1.0.
        output_path (str): Path to save the screenshot. Defaults to an auto-generated file if not specified.
    """

    def __init__(self, 
                 web: bool = False, 
                 locate: str = "", 
                 first: bool = False, 
                 delay: int = 0, 
                 additional_css: str = "", 
                 additional_js: str = "",
                 viewport: dict = {}, 
                 full_screen: bool = False, 
                 hide_classes: list = [],
                 device_scale_factor: float = 1.0,
                 output_path: str = ""):
        self.web = web
        self.locate = locate
        self.first = first
        self.delay = delay
        self.additional_css = additional_css
        self.additional_js = additional_js
        self.viewport: Dict[Literal["width", "height"], int] = viewport or {"width": 1920, "height": 1080}
        self.full_screen = full_screen
        self.hide_classes = hide_classes or []
        self.device_scale_factor = device_scale_factor
        self.output_path = output_path

class ScreenshotGenerator:
    _browser: Browser | Any = None
    _context: BrowserContext | Any = None
    _playwright: Any | None = None


    @classmethod
    async def launch(cls):
        if cls._browser is None:
            cls._playwright = await async_playwright().start()
            cls._browser = await cls._playwright.chromium.launch(headless=True)
            cls._context = await cls._browser.new_context()
            logger.info("Playwright 已载入")

    @classmethod
    async def close(cls):
        if cls._context:
            await cls._context.close()
            cls._context = None
        if cls._browser:
            await cls._browser.close()
            await cls._playwright.stop() # type: ignore
            cls._browser = None
            cls._playwright = None

    async def generate(self, config: ScreenshotConfig, page_source: str):
        """
        根据配置生成截图。
        """
        if self._browser is None or self._context is None:
            raise BrowserNotInitializedException()

        page = await self._browser.new_page(viewport=config.viewport) # type: ignore
        await page.goto(page_source)  # 使用 page_source 加载页面

        # 应用自定义的 CSS 和 JS
        await self._apply_customizations(page, config)

        # 保存截图
        screenshot_path = await self._save_screenshot(page, config)
        
        # 关闭页面
        await page.close()

        return screenshot_path

    async def _apply_customizations(self, page, config: ScreenshotConfig):
        """
        根据配置应用额外的自定义样式和脚本。
        """
        if config.delay > 0:
            await asyncio.sleep(config.delay / 1000)
        if config.additional_css:
            await page.add_style_tag(content=config.additional_css)
        if config.additional_js:
            await page.evaluate(config.additional_js)
        if config.hide_classes:
            combined_selector = ', '.join(f'.{cls}' for cls in config.hide_classes)
            await page.evaluate(f"document.querySelectorAll('{combined_selector}').forEach(el => el.style.display = 'none')")

    async def _save_screenshot(self, page, config: ScreenshotConfig):
        """
        保存截图到指定路径。
        """
        output_path = config.output_path or f"{CACHE}/{get_uuid()}.png"
        if config.locate:
            locator = page.locator(config.locate)
            if config.first:
                locator = locator.first
            await locator.screenshot(path=output_path)
        else:
            await page.screenshot(path=output_path, full_page=config.full_screen)
        return output_path

@time_record
async def generate(
    source: str,
    locate: str = "",
    first: bool = False,
    delay: int = 0,
    additional_css: str = "",
    additional_js: str = "",
    viewport: dict = {},
    full_screen: bool = False,
    hide_classes: list = [],
    device_scale_factor: float = 1.0,
    output_path: str = ""
):
    """
    Args:
        source (str): 可以是 HTML 源代码、文件路径或者 URL。
        locate (str): 用于指定要截图的元素 CSS 选择器，若为空则截图整个页面。
        first (bool): 是否只截取匹配的第一个元素。
        delay (int): 截图前的延迟时间（毫秒）。
        additional_css (str): 自定义的 CSS 样式。
        additional_js (str): 自定义的 JavaScript 脚本。
        viewport (dict): 浏览器视窗尺寸。
        full_screen (bool): 是否截取全页面。
        hide_classes (list): 需要隐藏的元素类名。
        device_scale_factor (float): 设备像素比。
        output_path (str): 保存截图的路径。
    """
    
    # 确定 source 类型
    web = source.startswith("http")  # 如果是 URL
    is_html = "<html" in source.lower()  # 如果是 HTML 源代码

    if is_html:
        # 创建缓存文件路径
        html_file_path = build_path(CACHE, [get_uuid() + ".html"])
        
        # 将 HTML 源代码写入缓存文件
        write(html_file_path, source)
        
        # 将文件路径作为 page_source 传递
        page_source = Path(html_file_path).as_uri()
    elif web:
        page_source = source  # 作为 URL 加载
    else:
        raise ValueError("Invalid source: must be HTML, or web URL.")

    config = ScreenshotConfig(
        web=web,
        locate=locate,
        first=first,
        delay=delay,
        additional_css=additional_css,
        additional_js=additional_js,
        viewport=viewport,
        full_screen=full_screen,
        hide_classes=hide_classes,
        device_scale_factor=device_scale_factor,
        output_path=output_path
    )
    
    generator = ScreenshotGenerator()
    return await generator.generate(config, page_source)
