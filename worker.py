import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio import workflow


with workflow.unsafe.imports_passed_through():
    from workflow import SayHelloWorkflow
    from activity import greet


async def main():
    # Create the Temporal client
    client = await Client.connect("localhost:7233")

    # Create and start the worker
    worker = Worker(
        client,
        task_queue="hello-world",
        workflows=[SayHelloWorkflow],
        activities=[greet],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
