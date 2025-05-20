# actionapi/management/commands/update_all_customers_from_sheets.py
import time
from django.core.management.base import BaseCommand, CommandError
from actionapi.models import Customer  # Make sure this path is correct
from actionapi.utils.sheet_updater import update_customer_from_sheet  # Correct path
from django.conf import settings  # For any settings you might need


class Command(BaseCommand):
    help = "Updates all customers from their linked Google Sheets daily."

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("Starting daily customer sheet update process...")
        )

        customers = Customer.objects.all()
        total_customers = customers.count()
        updated_count = 0
        failed_count = 0

        if not customers:
            self.stdout.write(self.style.WARNING("No customers found to update."))
            return

        self.stdout.write(f"Found {total_customers} customers to process.")

        for customer in customers:
            self.stdout.write(
                f"Processing customer DID: {customer.did_number}, Name: {customer.name}..."
            )
            try:
                # The 'created' flag is False because we are updating existing customers.
                # The update_customer_from_sheet function handles the actual fetching
                # and saving of new data from the sheet.
                result = update_customer_from_sheet(customer, created=False)

                if result.get("status") == "success":
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully updated customer {customer.did_number}. "
                            f"Message: {result.get('message', '')}"
                        )
                    )
                    updated_count += 1
                else:
                    self.stderr.write(
                        self.style.ERROR(
                            f"Failed to update customer {customer.did_number}. "
                            f"Error: {result.get('error', 'Unknown error from sheet_updater')}"
                        )
                    )
                    failed_count += 1
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        f"Critical error updating customer {customer.did_number}: {e}"
                    )
                )
                failed_count += 1

            # Optional: add a small delay to avoid hitting API rate limits too hard if you have many customers
            # time.sleep(1) # e.g., 1 second delay

        self.stdout.write(self.style.SUCCESS("------------------------------------"))
        self.stdout.write(
            self.style.SUCCESS("Daily customer sheet update process finished.")
        )
        self.stdout.write(f"Total customers processed: {total_customers}")
        self.stdout.write(self.style.SUCCESS(f"Successfully updated: {updated_count}"))
        self.stdout.write(self.style.ERROR(f"Failed updates: {failed_count}"))

        if failed_count > 0:
            self.stdout.write(
                self.style.WARNING("Some customers failed to update. Check logs above.")
            )
