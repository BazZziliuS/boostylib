"""Sync proxy that wraps async API modules."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any


class SyncProxy:
    """Wraps an async API module, making all async methods synchronous.

    Each method call is dispatched to the background event loop
    and blocks until the result is available.
    """

    def __init__(self, async_obj: Any, runner: Callable[..., Any]) -> None:
        self._async_obj = async_obj
        self._runner = runner

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self._async_obj, name)
        if inspect.iscoroutinefunction(attr):

            def sync_method(*args: Any, **kwargs: Any) -> Any:
                return self._runner(attr(*args, **kwargs))

            sync_method.__name__ = name
            sync_method.__doc__ = attr.__doc__
            return sync_method
        return attr
