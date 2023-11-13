from .. import *


def test_retry():
    now_count = {'v': -1}

    @use_retry()
    def inner():
        now_count['v'] += 1
        print(1 / now_count['v'])
    inner()
