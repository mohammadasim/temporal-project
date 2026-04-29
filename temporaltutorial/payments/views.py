from django.shortcuts import render
from temporalio.client import Client
import uuid


def index(request):
    return render(request, "payments/index.html")


async def trigger_workflow(request):
    """
    POST handler that triggers a Temporal workflow.
    Replace the placeholder below with your own workflow client call.
    """
    result = None
    error = None

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        course_name = request.POST.get("course_name", "").strip()
        course_price = request.POST.get("course_price", "").strip()

        if name and email and course_name and course_price:
            try:
                client = await Client.connect("localhost:7233")
                workflow_result = await client.execute_workflow(
                    "EnrollmentWorkflow",
                    args=[name, email, course_name, float(course_price)],
                    id=f"enrollment-{name}-{uuid.uuid4()}",
                    task_queue="learnflow-queue",
                )
                result = (
                    f"Workflow triggered for {name} ({email}) "
                    f"enrolling in '{course_name}' at £{course_price}\n"
                    f"Workflow result: {workflow_result}"
                )
            except Exception as exc:
                error = str(exc)
        else:
            error = "Please fill in all fields."

    return render(request, "payments/index.html", {"result": result, "error": error})
