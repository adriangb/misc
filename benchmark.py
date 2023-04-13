import time
from dataclasses import dataclass

import anyio
import httpx
import numpy as np


async def worker(urls: list[str], requests_durations: list[float]) -> None:
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(None)
    ) as client:
        while urls:
            url = urls.pop()
            start = time.time()
            resp = await client.get(url)
            end = time.time()
            requests_durations.append(end-start)
            resp.raise_for_status()


@dataclass
class Result:
    elapsed: float
    throughput: float
    requests_durations: list[float]

async def run_test(url: str, n_requests: int, n_workers: int) -> Result:
    requests = [url] * n_requests
    start = time.time()
    requests_durations: list[float] = []
    async with anyio.create_task_group() as tg:
        for _ in range(n_workers):
            tg.start_soon(worker, requests, requests_durations)
    end = time.time()
    elapsed = end - start
    return Result(elapsed, len(requests_durations)/elapsed, requests_durations)


async def main() -> None:
    urls = {"gunicorn": "http://34.69.142.42:80", "uvicorn": "http://34.30.96.230:80"}
    tests = {"io": "/do_io?time_s=1", "cpu": "/do_cpu?time_s=5", "nothing": "/do_io?time_s=0"}
    for test_name, test_url_suffix in tests.items():
        for target, url in urls.items():
            full_url = f"{url}{test_url_suffix}"
            res = await run_test(full_url, n_requests=128, n_workers=128)
            latency_avg, latency_std = np.average(res.requests_durations), np.std(res.requests_durations)
            print(f"{target} - {test_name}: {res.throughput:.2f} req/s, {latency_avg:.2f}±{latency_std:.2f} s/req")
 

if __name__ == "__main__":
    anyio.run(main)
