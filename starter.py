import asyncio
import uuid
from temporalio.client import Client


async def main():
    # Create the Temporal client
    client = await Client.connect("localhost:7233")

    # Start the SayHelloWorkflow with a unique workflow ID and a name argument
    result = await client.execute_workflow(
        "SayHelloWorkflow",
        "Mohammad",
        id=f"say-hello-{uuid.uuid4()}",
        task_queue="hello-world",
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
