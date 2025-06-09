# actionapi/tasks.py
import logging

from celery import shared_task

from .models import Customer
from .utils.sheet_updater import update_customer_from_sheet

# Get a logger instance
logger = logging.getLogger(__name__)


@shared_task(name="actionapi.tasks.update_all_customers_task")
def update_all_customers_task():
    """
    Celery task to update all customers from their linked Google Sheets.
    """
    logger.info("Celery Task: Starting daily customer sheet update process...")

    customers = Customer.objects.all()
    total_customers = customers.count()
    updated_count = 0
    failed_count = 0

    if not customers:
        logger.warning("Celery Task: No customers found to update.")
        return "Process finished: No customers found."

    logger.info(f"Celery Task: Found {total_customers} customers to process.")

    for customer in customers:
        logger.info(
            f"Celery Task: Processing customer DID: {customer.did_number}, Name: {customer.name}..."
        )
        try:
            result = update_customer_from_sheet(customer, created=False)

            if result.get("status") == "success":
                logger.info(
                    f"Celery Task: Successfully updated customer {customer.did_number}. "
                    f"Message: {result.get('message', '')}"
                )
                updated_count += 1
            else:
                logger.error(
                    f"Celery Task: Failed to update customer {customer.did_number}. "
                    f"Error: {result.get('error', 'Unknown error')}"
                )
                failed_count += 1
        except Exception as e:
            logger.error(
                f"Celery Task: Critical error updating customer {customer.did_number}: {e}",
                exc_info=True,  # This will include the full traceback in the log
            )
            failed_count += 1

    summary = (
        f"Daily customer sheet update process finished. "
        f"Total processed: {total_customers}, "
        f"Successfully updated: {updated_count}, "
        f"Failed updates: {failed_count}."
    )
    logger.info(f"Celery Task: {summary}")

    return summary
