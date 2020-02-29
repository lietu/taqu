import os
import signal
import time
from asyncio import run, sleep
from multiprocessing import Queue, Process
from random import randint

from pydantic import BaseModel

from settings import CONNECTION_STRING, QUEUE
from taqu.aio import TaquAzureWorker

NUM_WORKERS = os.cpu_count() + 1
WORKERS = [f"worker-{i}" for i in range(1, NUM_WORKERS + 1)]
QUEUES = {}

for worker_id in WORKERS:
    queue = Queue()
    QUEUES[worker_id] = queue


class CreateUser(BaseModel):
    username: str


async def create_user(params: CreateUser):
    if randint(1, 5) <= 2:  # nosec
        print("Random failure")
        raise ValueError(f"Random error processing {params.username}")

    for i in range(1, 5):
        print(f"{params.username} update {i}")
        await sleep(5.0)


async def main(exit_queue: Queue, worker_id: str):
    worker = TaquAzureWorker(CONNECTION_STRING, QUEUE, worker_id)
    await worker.register(create_user)
    await worker.run(exit_queue)


def _worker_init():
    # Ignore CTRL+C in workers
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def _start_worker(queue, worker_id):
    print(f"Starting worker {worker_id}")
    _worker_init()
    run(main(queue, worker_id))


if __name__ == "__main__":
    # Ignore SIGINT in child processes
    orig_sigint = signal.signal(signal.SIGINT, signal.SIG_IGN)

    processes = {}
    try:
        for worker_id in WORKERS:
            queue = Queue()
            p = Process(target=_start_worker, name=worker_id, args=(queue, worker_id))
            QUEUES[worker_id] = queue
            processes[worker_id] = p
            p.daemon = True
            p.start()

        # Restore SIGINT handler in main process
        signal.signal(signal.SIGINT, orig_sigint)

        print("Workers started.")

        while True:
            # Just wait until we want to stop
            time.sleep(1)
    except KeyboardInterrupt:
        print("Caught CTRL+C, terminating workers...")

        for worker_id in WORKERS:
            QUEUES[worker_id].put(True, block=False)

    # Wait for all workers to quit
    for worker_id in processes:
        processes[worker_id].join()
