from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from payments.activities import (
        process_payment,
        send_confirmation_email,
        update_enrollment_status,
        create_invoice,
        email_invoice,
    )


@workflow.defn
class EnrollmentWorkflow:
    @workflow.run
    async def run(
        self, name: str, email: str, course_name: str, course_price: float
    ) -> str:
        # Step 1: Process the payment
        payment_result = await workflow.execute_activity(
            process_payment,
            args=[name, email, course_name, course_price],
            schedule_to_close_timeout=timedelta(seconds=10),
        )

        # Step 2: Send confirmation email
        email_result = await workflow.execute_activity(
            send_confirmation_email,
            args=[name, email, course_name],
            schedule_to_close_timeout=timedelta(seconds=10),
        )

        # Step 3: Update enrollment status
        enrollment_result = await workflow.execute_activity(
            update_enrollment_status,
            args=[name, course_name],
            schedule_to_close_timeout=timedelta(seconds=10),
        )

        # Step 4: Create invoice
        invoice_result = await workflow.execute_activity(
            create_invoice,
            args=[name, course_name, course_price],
            schedule_to_close_timeout=timedelta(seconds=10),
        )

        # Step 5: Email the invoice
        email_invoice_result = await workflow.execute_activity(
            email_invoice,
            args=[name, email, course_name],
            schedule_to_close_timeout=timedelta(seconds=10),
        )

        return (
            f"{payment_result}\n{email_result}\n{enrollment_result}\n"
            f"{invoice_result}\n{email_invoice_result}"
        )
