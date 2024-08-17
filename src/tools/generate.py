from playwright.async_api import async_playwright
from pathlib import Path
from nonebot.log import logger
from src.tools.utils.path import CACHE
import uuid
import asyncio
import time

def get_uuid():
    return str(uuid.uuid1()).replace("-", "")

class ScreenshotGenerator:
    def __init__(
            self, 
            path: str,
            web: bool = False, 
            locate: str = None, 
            first: bool = False, 
            delay: int = 0, 
            additional_css: str = "", 
            additional_js: str = "",
            viewport: dict = None, 
            full_screen: bool = False, 
            hide_classes: list = [],
            device_scale_factor: float = 1.0,
            output_path: str = None,
        ):
        self.path = Path(path).as_uri() if not web else path
        self.web = web
        self.locate = locate
        self.first = first
        self.delay = delay
        self.additional_css = additional_css or ""
        self.additional_js = additional_js or ""
        self.viewport = viewport or {}
        self.full_screen = full_screen
        self.hide_classes = hide_classes
        self.device_scale_factor = device_scale_factor
        self.output_path = output_path
        self.uuid = get_uuid()

    async def _launch_browser(self, playwright):
        return await playwright.chromium.launch(headless=True, slow_mo=0)

    async def _setup_context_and_page(self, browser):
        context = await browser.new_context(device_scale_factor=self.device_scale_factor, viewport=self.viewport if self.viewport else None)
        page = await context.new_page()
        await page.goto(self.path)
        return page

    async def _apply_customizations(self, page):
        if self.delay > 0:
            await asyncio.sleep(self.delay / 1000)
        if self.web:
            if self.additional_css:
                print(1)
                await page.add_style_tag(content=self.additional_css)
        if self.additional_js:
            await page.evaluate(self.additional_js)
        if self.hide_classes:
            await self._hide_elements_by_class(page)

    async def _hide_elements_by_class(self, page):
        if self.hide_classes:
            combined_selector = ', '.join(f'.{cls}' for cls in self.hide_classes)
            await page.evaluate(f"document.querySelectorAll('{combined_selector}').forEach(el => el.style.display = 'none')")

    async def _capture_element_screenshot(self, locator, store_path):
        if self.first:
            locator = locator.first
        await locator.screenshot(path=store_path)

    async def _capture_full_screenshot(self, page, store_path):
        await page.screenshot(path=store_path, full_page=self.full_screen)

    async def _save_screenshot(self, page, store_path):
        store_path = f"{CACHE}/{self.uuid}.png" if not store_path else store_path
        if self.locate:
            locator = page.locator(self.locate)
            await self._capture_element_screenshot(locator, store_path)
        else:
            await self._capture_full_screenshot(page, store_path)
        return store_path

    async def generate(self):
        try:
            time_start = time.time()
            logger.opt(colors=True).info(f"<green>Generating source: {self.path}</green>")

            async with async_playwright() as p:
                browser = await self._launch_browser(p)
                page = await self._setup_context_and_page(browser)
                await self._apply_customizations(page)
                store_path = await self._save_screenshot(page, self.output_path)

            time_end = time.time()
            logger.opt(colors=True).info(f"<green>Generated successfully: {store_path}, spent {round(time_end - time_start, 2)}s</green>")
            return store_path

        except Exception as ex:
            logger.error(f"图片生成失败，请尝试执行 `playwright install`！: {ex}")
            return False

async def generate(
    path: str,
    web: bool = False,
    locate: str = None,
    first: bool = False,
    delay: int = 0,
    additional_css: str = "",
    additional_js: str = "",
    viewport: dict = None,
    full_screen: bool = False,
    hide_classes: list = None,
    device_scale_factor: float = 1.0,
    output: str = ""
):
    generator = ScreenshotGenerator(path, web, locate, first, delay, additional_css, additional_js, viewport, full_screen, hide_classes, device_scale_factor, output)
    return await generator.generate()
