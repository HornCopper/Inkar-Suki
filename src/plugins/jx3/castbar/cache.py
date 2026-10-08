"""Thread-safe LRU storage bounded by both entry count and byte size."""
from collections import OrderedDict
import threading


class ByteCache:
    def __init__(self, max_bytes: int, max_entries: int):
        self.max_bytes = max_bytes
        self.max_entries = max_entries
        self._entries = OrderedDict()
        self._bytes = 0
        self._lock = threading.Lock()

    def get(self, key):
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            self._entries.move_to_end(key)
            return entry[0]

    def put(self, key, value, size: int):
        if size > self.max_bytes:
            return
        with self._lock:
            previous = self._entries.pop(key, None)
            if previous is not None:
                self._bytes -= previous[1]
            self._entries[key] = (value, size)
            self._bytes += size
            while self._bytes > self.max_bytes or len(self._entries) > self.max_entries:
                _, (_, removed_size) = self._entries.popitem(last=False)
                self._bytes -= removed_size
