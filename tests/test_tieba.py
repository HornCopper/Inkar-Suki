from . import *
import asyncio


def test_fetch_threads():
    from src.tools.tieba import client
    threads = asyncio.run(client.run_once())
    threads_count = len(threads)
    assert threads_count > 0, 'threads return should have content'
    client.current_status.last_thread_index -= 1
    threads2 = asyncio.run(client.run_once())
    assert len(threads2) > threads_count, 'thread count of 2 page should more than 1 page\'s'
