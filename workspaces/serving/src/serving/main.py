from typing import Annotated
import anyio

from fastapi import FastAPI, Query, Response


def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True

def generate_primes_up_to(n: int) -> list[int]:
    """Returns  a list of primes < n

    This is _extremely_ inefficient but the goal here
    is to burn CPU while not using much memory, so it is
    exactly what we want.
    """
    return [i for i in range(n) if is_prime(i)]


app = FastAPI()


@app.get("/do_cpu")
async def calculate_primes(
    n: Annotated[int, Query()],
) -> list[int]:
    """An extremely inefficient method to find prime numbers.

    The goal of this endpoint is to simulate CPU bound work.
    """
    return [i for i in range(n) if is_prime(i)]


@app.get("/do_io")
async def sleep(
    time: Annotated[float, Query()]
) -> Response:
    """An endpoint that does IO sleeping / waiting.
    """
    await anyio.sleep(time)
    return Response(status_code=200)
