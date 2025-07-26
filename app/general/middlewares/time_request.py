import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from ..utils import config

class TimeRequestsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        Middleware to record request time
        """
        start_time = time.perf_counter_ns()

        response = await call_next(request)

        process_time = time.perf_counter_ns() - start_time

        response.headers[config.PROCESS_TIME_HEADER] = str(process_time)

        return response