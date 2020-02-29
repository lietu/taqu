from json import dumps

from pydantic import BaseModel

from taqu.exceptions import TaquException
from taqu.utils import logger

try:
    from azure.servicebus.aio import ServiceBusClient, Message
except ImportError:
    ServiceBusClient = None
    Message = None


class _TaquAsyncClient:
    def __init__(self):
        pass

    async def _send(self, payload):
        raise NotImplementedError("Taqu client _send not implemented")

    async def close(self):
        pass

    async def send(self, task: BaseModel):
        if not issubclass(task.__class__, BaseModel):
            raise TaquException("Taqu can only send pydantic models as tasks")

        data = task.dict()
        payload = dumps({"name": task.__class__.__name__, "data": data})

        logger.info("Sending %s", payload)

        await self._send(payload)


class TaquAzureClient(_TaquAsyncClient):
    def __init__(self, connection_string: str, queue: str):
        if not ServiceBusClient or not Message:
            raise TaquException(
                "Cannot use TaquAzureClient without azure-servicebus package."
            )

        self.connection_string = connection_string
        self.queue = queue
        self._client = ServiceBusClient.from_connection_string(connection_string)
        self._queue = self._client.get_queue(self.queue)
        self._sender = None
        super().__init__()

    def _get_sender(self):
        if not self._sender:
            self._sender = self._queue.get_sender()

        return self._sender

    async def _send(self, payload: bytes):
        msg = Message(payload)
        sender = self._get_sender()
        await sender.send(msg)

    async def close(self):
        if self._sender:
            await self._sender.close()
