from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activity import greet


@workflow.defn
class SayHelloWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        # Call the greet activity with a timeout of 10 seconds
        return await workflow.execute_activity(
            greet,
            name,
            schedule_to_close_timeout=timedelta(seconds=10),
        )
