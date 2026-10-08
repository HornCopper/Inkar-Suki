"""Exercise castbar rendering and queued generation without starting the bot."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
import importlib
import io
from pathlib import Path
import sys
import threading
import types
import unittest
from unittest.mock import AsyncMock, patch

from PIL import Image, ImageChops, ImageStat


package = types.ModuleType('castbar_under_test')
package.__path__ = [str(Path(__file__).resolve().parents[1] / 'src/plugins/jx3/castbar')]
sys.modules[package.__name__] = package
app = importlib.import_module(package.__name__ + '.app')
ByteCache = importlib.import_module(package.__name__ + '.cache').ByteCache


class CastbarCacheTests(unittest.TestCase):
    def test_byte_budget_evicts_least_recently_used(self):
        cache = ByteCache(max_bytes=6, max_entries=3)
        cache.put('a', b'aaa', 3)
        cache.put('b', b'bb', 2)
        self.assertEqual(cache.get('a'), b'aaa')
        cache.put('c', b'ccc', 3)
        self.assertIsNone(cache.get('b'))
        self.assertEqual(cache.get('a'), b'aaa')
        cache.put('large', b'1234567', 7)
        self.assertIsNone(cache.get('large'))
        self.assertEqual(cache.get('c'), b'ccc')

    def test_entry_budget_and_replacement(self):
        cache = ByteCache(max_bytes=8, max_entries=2)
        cache.put('a', b'aaaa', 4)
        cache.put('a', b'a', 1)
        cache.put('b', b'bbbb', 4)
        self.assertEqual(cache.get('a'), b'a')
        cache.put('c', b'c', 1)
        self.assertIsNone(cache.get('b'))
        self.assertEqual(cache.get('a'), b'a')

    def test_equivalent_requests_reuse_output_but_format_is_separate(self):
        with patch.object(app, 'IMAGE_CACHE', ByteCache(1024 * 1024, 8)):
            original = app.generate_image('changge format=png particles=off')
            with patch.object(app.renderer, 'render', side_effect=AssertionError('cache miss')):
                repeated = app.generate_image('school=changge particles=off format=png')
            self.assertIs(original, repeated)
            animated = app.generate_image('changge duration=0.1 format=gif particles=off')
            self.assertTrue(animated.content.startswith(b'GIF'))

    def test_cached_sprites_preserve_pixels_across_animation_frames(self):
        data, _ = app.parse_request('qixiu direction=reverse duration=1')
        before = app.renderer.render(data, 0.3).tobytes()
        app.renderer.render(data, 0.7)
        self.assertEqual(app.renderer.render(data, 0.3).tobytes(), before)

    def test_exported_animations_have_expected_duration_and_size(self):
        for format_ in ['gif', 'apng']:
            with self.subTest(format=format_):
                result = app.generate_image(f'changge duration=0.2 format={format_}')
                with Image.open(io.BytesIO(result.content)) as image:
                    style = app.renderer.BY_ID['changge']
                    self.assertEqual(image.size, (style['width'] * 2, style['height'] * 2))
                    total = 0
                    for frame in range(image.n_frames):
                        image.seek(frame)
                        total += image.info['duration']
                    self.assertAlmostEqual(total, 200, delta=1)

    def test_gif_preserves_transparency_and_limits_color_error(self):
        for school in ['changge', 'qixiu', 'wanhua']:
            with self.subTest(school=school):
                data, _ = app.parse_request(f'{school} duration=0.2 direction=reverse')
                times, _ = app.renderer.animation_plan(data, 10)
                with Image.open(io.BytesIO(app.renderer.gif_bytes(data))) as image:
                    self.assertEqual(image.n_frames, len(times))
                    for index, elapsed in enumerate(times):
                        image.seek(index)
                        actual = image.convert('RGBA')
                        target = app.renderer.render(data, elapsed)
                        mask = target.getchannel('A').point(lambda a: 255 if a >= 96 else 0)
                        self.assertIsNone(ImageChops.difference(actual.getchannel('A'), mask).getbbox())
                        difference = ImageChops.difference(actual.convert('RGB'), target.convert('RGB'))
                        self.assertLess(max(ImageStat.Stat(difference, mask).mean), 6)


class CastbarQueueTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.executor_patch = patch.object(app, '_RENDER_EXECUTOR', self.executor)
        self.queue_patch = patch.object(app, '_QUEUED_JOBS', [])
        self.executor_patch.start()
        self.queue_patch.start()
        self.release = threading.Event()
        self.started = asyncio.Event()
        self.loop = asyncio.get_running_loop()
        self.calls = []

    async def asyncTearDown(self):
        self.release.set()
        self.executor.shutdown(wait=True)
        self.queue_patch.stop()
        self.executor_patch.stop()

    def render(self, text):
        self.calls.append(text)
        if text == 'first':
            self.loop.call_soon_threadsafe(self.started.set)
            if not self.release.wait(3):
                raise TimeoutError('test did not release the worker')
        if text == 'bad':
            raise ValueError('invalid request')
        return app.GeneratedImage(text.encode(), text + '.png', 'png')

    async def start_first(self):
        task = asyncio.create_task(app.generate_image_async('first'))
        await asyncio.wait_for(self.started.wait(), 1)
        return task

    async def test_fifo_queue_notices_and_event_loop_remains_responsive(self):
        notify = AsyncMock()
        with patch.object(app, 'generate_image', self.render):
            first = await self.start_first()
            second = asyncio.create_task(app.generate_image_async('second', notify))
            await asyncio.sleep(0)
            third = asyncio.create_task(app.generate_image_async('third', notify))
            await asyncio.sleep(0)
            self.assertEqual(self.calls, ['first'])
            self.assertEqual([call.args[0] for call in notify.await_args_list], [1, 2])
            self.release.set()
            results = await asyncio.wait_for(asyncio.gather(first, second, third), 2)
            self.assertEqual(self.calls, ['first', 'second', 'third'])
            self.assertEqual([result.content for result in results], [b'first', b'second', b'third'])
            self.assertEqual(app._QUEUED_JOBS, [])

    async def test_ordinary_command_information_does_not_yield_before_queueing(self):
        with patch.object(app.asyncio, 'to_thread', side_effect=AssertionError('unexpected yield')):
            self.assertIsNone(await app.information_async('changge'))
            self.assertIn('GIF', await app.information_async('help'))

    async def test_failed_job_does_not_stop_next_job(self):
        with patch.object(app, 'generate_image', self.render):
            first = await self.start_first()
            bad = asyncio.create_task(app.generate_image_async('bad'))
            good = asyncio.create_task(app.generate_image_async('good'))
            await asyncio.sleep(0)
            self.release.set()
            results = await asyncio.wait_for(asyncio.gather(first, bad, good, return_exceptions=True), 2)
            self.assertIsInstance(results[1], ValueError)
            self.assertEqual(results[2].content, b'good')

    async def test_cancelling_running_job_does_not_start_next_early(self):
        with patch.object(app, 'generate_image', self.render):
            first = await self.start_first()
            second = asyncio.create_task(app.generate_image_async('second'))
            await asyncio.sleep(0)
            first.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await first
            self.assertEqual(self.calls, ['first'])
            self.release.set()
            self.assertEqual((await asyncio.wait_for(second, 2)).content, b'second')

    async def test_cancelling_waiting_job_skips_it(self):
        with patch.object(app, 'generate_image', self.render):
            first = await self.start_first()
            second = asyncio.create_task(app.generate_image_async('second'))
            third = asyncio.create_task(app.generate_image_async('third'))
            await asyncio.sleep(0)
            second.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await second
            self.release.set()
            await asyncio.wait_for(asyncio.gather(first, third), 2)
            self.assertEqual(self.calls, ['first', 'third'])


if __name__ == '__main__':
    unittest.main()
