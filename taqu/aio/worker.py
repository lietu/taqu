from contextlib import asynccontextmanager
from inspect import signature, iscoroutinefunction
from json import loads
from multiprocessing import Queue
from queue import Empty
from typing import Callable, AsyncIterable

from azure.servicebus.aio.async_client import QueueClient
from pydantic.main import ModelMetaclass

from taqu.exceptions import TaquException
from taqu.utils import logger

try:
    from azure.servicebus.aio import ServiceBusClient, Message
except ImportError:
    ServiceBusClient = None
    Message = None

POLL_INTERVAL = 1 / 8


class _TaquWorker:
    def __init__(self, worker_id: str = "worker-1"):
        self._tasks = {}
        self._models = {}
        self._worker_id = worker_id

    async def register(self, task: Callable):
        sig = signature(task)
        if len(sig.parameters) != 1:
            raise TaquException("Taqu tasks should take one argument, a pydantic model")

        if not iscoroutinefunction(task):
            raise TaquException("Tasks for taqu.aio need to be awaitable (async def)")

        for param_name in sig.parameters:
            param = sig.parameters[param_name]
            annot = param.annotation
            if not issubclass(annot.__class__, ModelMetaclass):
                raise TaquException(
                    "Taqu tasks should take a pydantic model as their only argument"
                )

            model_name = annot.__name__

            logger.info(
                "%s: Registering %s handler for %s tasks",
                self._worker_id,
                task.__name__,
                model_name,
            )
            self._tasks[model_name] = task
            self._models[model_name] = annot

    async def _get_tasks(self) -> AsyncIterable[bytes]:
        raise NotImplementedError("_get_tasks not implemented for Taqu worker class")

    @asynccontextmanager
    async def _handle_message(self, message):
        yield

    async def run(self, exit_queue: Queue = None):
        if not self._tasks:
            raise TaquException("Trying to run Taqu worker without registered tasks.")

        logger.info(
            "%s running with %d registered tasks", self._worker_id, len(self._tasks)
        )

        async for message in self._get_tasks(exit_queue):
            logger.info("%s: Received %s task", self._worker_id, message["name"])
            async with self._handle_message(message):
                handler = self._tasks[message["name"]]
                data = self._models[message["name"]](**message["data"])
                await handler(data)


class TaquAzureWorker(_TaquWorker):
    def __init__(self, connection_string: str, queue: str, worker_id: str = "worker-1"):
        if not ServiceBusClient or not Message:
            raise TaquException(
                "Cannot use TaquAzureWorker without azure-servicebus package."
            )

        self.connection_string = connection_string
        self.queue = queue
        self._client = ServiceBusClient.from_connection_string(connection_string)
        self._abandoned = False
        self._current_message = None
        super().__init__(worker_id)

    @asynccontextmanager
    async def _handle_message(self, message):
        self._abandoned = False
        try:
            yield
        except Exception as e:
            logger.exception(
                "%s: Caught %s while processing message, releasing lock and trying again.",
                self._worker_id,
                e.__class__.__name__,
            )
            await self._current_message.abandon()
            self._abandoned = True

        # TODO: Maybe a RescheduleException?
        self._current_message = None

    async def _get_tasks(self, exit_queue: Queue = None) -> AsyncIterable[bytes]:
        queue_client = self._client.get_queue(self.queue)  # type: QueueClient
        async with queue_client.get_receiver() as receiver:
            while True:
                messages = await receiver.fetch_next(1, POLL_INTERVAL)
                if messages:
                    message = messages[0]
                    payload = loads(str(message))
                    if payload["name"] in self._tasks:
                        self._current_message = message
                        yield payload
                        if not self._abandoned:
                            await message.complete()
                    else:
                        logger.debug(
                            "%s: Skipping unsupported task %s",
                            self._worker_id,
                            payload["name"],
                        )
                        await message.abandon()

                try:
                    exit_queue.get(block=False)
                    return
                except Empty:
                    pass
