from contextlib import asynccontextmanager
from typing import Any, AsyncIterator
from fastapi import FastAPI
import numpy as np
import psutil

n_requests = 0


def print_memory_usage_mb() -> None:
    current_process = psutil.Process()
    memory: int = current_process.memory_info().rss
    mem_use_mb = int(memory / (1024 * 1024))
    print(f"{current_process.pid} @ {n_requests}: {mem_use_mb} Mb")


# make a large list and try to share it
weights: list[float] = np.random.random(size=(10_000_000,)).tolist()


@asynccontextmanager
async def lifespan(_: Any) -> AsyncIterator[None]:
    print_memory_usage_mb()
    yield


app = FastAPI(lifespan=lifespan)


print_memory_usage_mb()


@app.get("/do_stuff")
async def do_stuff() -> float:
    global n_requests
    n_requests += 1
    # read some of the shared memory
    x = 1
    for w in weights[:n_requests * 10]:
        x *= w
    print_memory_usage_mb()
    return x
