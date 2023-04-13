import gc
from time import time
from typing import Annotated, Any
import resource

import anyio
import numpy as np
from fastapi import FastAPI, Query, Response


def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True


app = FastAPI()


@app.get("/do_cpu")
async def burn_rubber(
    time_s: Annotated[float, Query()]
) -> Response:
    """Waste CPU for `time` seconds.
    """
    target = time() + time_s
    x = 1
    while time() < target:
        x *= 100
        x = x // 100
    return Response(status_code=200)



@app.get("/do_io")
async def sleep(
    time_s: Annotated[float, Query()]
) -> Response:
    """Sleep for `time` seconds.
    """
    await anyio.sleep(time_s)
    return Response(status_code=200)


n_requests = 0


def get_current_mem_usage_mb() -> int:
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024))


# make a large list and try to share it
weights_np: np.ndarray[Any, np.dtype[np.int64]] = np.random.random(size=(10_000_000,)).astype(np.int64)
weights_py: list[float] = np.random.random(size=(10_000_000,)).tolist()


@app.get("/access_py_memory")
async def measure_py_memory_increase() -> int:
    """
    Access a global object of Python data and measure the change
    in memory consumed (RSS) in mb.
    """
    before = get_current_mem_usage_mb()
    x = 1
    for y in weights_py:
        x *= y
    for gen in range(3):
        gc.collect(gen)
    after = get_current_mem_usage_mb()
    return after - before


@app.get("/access_np_memory")
async def measure_np_memory_increase() -> int:
    """
    Access a global object of Numpy data and measure the change
    in memory consumed (RSS) in mb.
    """
    before = get_current_mem_usage_mb()
    y = weights_np * 2
    del y
    for gen in range(3):
        gc.collect(gen)
    after = get_current_mem_usage_mb()
    return after - before
