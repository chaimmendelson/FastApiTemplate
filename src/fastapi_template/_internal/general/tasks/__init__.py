"""Background task registration for the FastAPI template."""

from collections.abc import Callable, Coroutine
from typing import List

from .uptime import update_uptime


def get_tasks(*, enable_uptime_background_task: bool = True) -> List[Callable[[], Coroutine]]:
    tasks: List[Callable[[], Coroutine]] = []

    if enable_uptime_background_task:
        tasks.append(update_uptime)

    return tasks
