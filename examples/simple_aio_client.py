from asyncio import run
from random import choice, randint
import sys

from pydantic import BaseModel

from settings import CONNECTION_STRING, QUEUE
from taqu.aio import TaquAzureClient

NAMES = [
    "Aiden",
    "Amelia",
    "Ava",
    "Barbara",
    "Benjamin",
    "Charles",
    "David",
    "Elijah",
    "Elizabeth",
    "Emma",
    "Ethan",
    "Isabella",
    "Jacob",
    "James",
    "Jennifer",
    "Jessica",
    "John",
    "Joseph",
    "Karen",
    "Liam",
    "Linda",
    "Logan",
    "Lucas",
    "Mary",
    "Mason",
    "Matthew",
    "Mia",
    "Michael",
    "Noah",
    "Olivia",
    "Patricia",
    "Richard",
    "Robert",
    "Sarah",
    "Sophia",
    "Susan",
    "Thomas",
    "William",
]


class CreateUser(BaseModel):
    username: str


async def main(num_tasks: int):
    client = TaquAzureClient(CONNECTION_STRING, QUEUE)
    for i in range(num_tasks):
        name = f"{choice(NAMES)}-{randint(1,1000)}"  # nosec
        await client.send(CreateUser(username=name))
    await client.close()


if __name__ == "__main__":
    run(main(int(sys.argv[1])))
