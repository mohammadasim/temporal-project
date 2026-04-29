"""
Temporal worker for the LearnFlow Django project.

Run with:
    python worker.py

This worker registers workflows and activities from all Django apps.
Add new apps' workflows and activities here as the project grows.
"""

import asyncio
import os

import django

# Bootstrap Django so that apps (and their models/settings) are available
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from temporalio.client import Client
from temporalio.worker import Worker

# ── payments app ──────────────────────────────────────────────────────────────
from payments.workflows import EnrollmentWorkflow
from payments.activities import (
    process_payment,
    send_confirmation_email,
    update_enrollment_status,
    create_invoice,
    email_invoice,
)

# Add imports from other apps here, e.g.:
# from certificates.workflows import IssueCertificateWorkflow
# from certificates.activities import generate_certificate, email_certificate

TASK_QUEUE = "learnflow-queue"


async def main():
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[
            EnrollmentWorkflow,
            # Add more workflow classes here as you create new apps
        ],
        activities=[
            process_payment,
            send_confirmation_email,
            update_enrollment_status,
            create_invoice,
            email_invoice,
            # Add more activity functions here as you create new apps
        ],
    )

    print(f"Worker started on task queue: '{TASK_QUEUE}'")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
