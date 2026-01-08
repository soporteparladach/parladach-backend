import logging
import time
from typing import Callable

from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("app.request")


async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
    """
    Log básico por request:
    - método
    - path
    - status
    - tiempo ms
    """
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000

    logger.info("%s %s -> %s (%.2fms)", request.method, request.url.path, response.status_code, elapsed_ms)
    return response
