"""Timing helpers."""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Iterator


@contextmanager
def timed() -> Iterator[callable]:
    """Context manager returning callable elapsed-seconds accessor."""
    start = time.perf_counter()
    yield lambda: time.perf_counter() - start
