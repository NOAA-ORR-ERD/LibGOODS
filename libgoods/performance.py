#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""Utilities for gauging performance."""
from ast import Call
from typing import Callable, Optional
import time
import platform


# Monotonic clocks are unaffected by system time changes and won't go backwards.
# If the system supports it, we want to use it.
if platform.system() == 'Windows':
    timing_func: Callable[[], float] = time.time
else:
    timing_func: Callable[[], float] = time.monotonic


class Timer:
    """A class to aid with measuring timing."""

    def __init__(self, msg=None, clock: Optional[Callable[[], float]] = None, output: Optional[Callable] = None):
        """Initializes the current time."""
        self.output = output or print
        self.clock = clock or timing_func
        self.t0 = self.clock()
        self.msg = msg

    def tick(self):
        """Update the timer start."""
        self.t0 = self.clock()

    def tock(self) -> float:
        """Return elapsed time in ms."""
        return (self.clock() - self.t0) * 1000.0

    def format(self):
        """return formatted time"""
        time_in_ms = self.tock()
        if time_in_ms > 60000:
            return f"{time_in_ms / 60000:.1f} min"
        if time_in_ms > 2000:
            return f"{time_in_ms / 1000:.1f} s"
        return f"{time_in_ms:.1f} ms"

    def __enter__(self):
        """With context."""
        self.tick()

    def __exit__(self, type, value, traceback):
        """With exit."""
        if self.msg is not None:
            self.output(self.msg.format(self.format()))