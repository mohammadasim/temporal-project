import asyncio
import os

from temporalio import activity
from temporalio.exceptions import ApplicationError

FLAG_FILE = "/tmp/email_activity_failed_once"


@activity.defn
async def process_payment(
    name: str, email: str, course_name: str, course_price: float
) -> str:
    """Simulate payment processing for a course enrollment."""
    print(f"Will start processing payment for {name}")
    await asyncio.sleep(5)
    print(f"A payment of £{course_price} has been processed for {course_name}.")
    return f"Payment processed for {name} ({email}) enrolling in '{course_name}' at £{course_price}"


@activity.defn
async def send_confirmation_email(name: str, email: str, course_name: str) -> str:
    """Simulate sending a confirmation email after payment."""
    print(f"Will start sending confirmation email to {email}")
    await asyncio.sleep(3)

    # Simulate failure on the first attempt, succeed on retry
    if not os.path.exists(FLAG_FILE):
        open(FLAG_FILE, "w").close()  # mark that we have failed once
        raise ApplicationError("Simulated transient email failure — will succeed on retry")
    # Second attempt onwards: clean up and succeed
    os.remove(FLAG_FILE)
    print(f"Confirmation email sent to {email} for enrolling in '{course_name}'.)")
    return f"Confirmation email sent to {email} for enrolling in '{course_name}'"


@activity.defn
async def update_enrollment_status(name: str, course_name: str) -> str:
    """Simulate updating the enrollment status in the database."""
    print(f"Will start updating enrollment status for {name}")
    await asyncio.sleep(2)
    print(f"Enrollment status updated for {name} in '{course_name}'.")
    return f"Enrollment status updated for {name} in '{course_name}'"


@activity.defn
async def create_invoice(name: str, course_name: str, course_price: float) -> str:
    """Simulate invoice creation after payment."""
    print(f"Will start creating invoice for {name}")
    await asyncio.sleep(4)
    print(f"Invoice created for {name} for '{course_name}' at £{course_price}.")
    return f"Invoice created for {name} for '{course_name}' at £{course_price}"


@activity.defn
async def email_invoice(name: str, email: str, course_name: str) -> str:
    """Simulate emailing the invoice to the user."""
    print(f"Will start emailing invoice to {email}")
    await asyncio.sleep(3)
    print(f"Invoice emailed to {email} for '{course_name}'.")
    return f"Invoice emailed to {email} for '{course_name}'"
