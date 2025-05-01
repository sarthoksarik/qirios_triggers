# actionapi/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.http import Http404  # Import Http404
from django.db import transaction  # Import transaction

# from django.db import transaction # Consider using transactions later if needed

from .models import Customer  # Assuming models are in the same app
from .serializers import CustomerSerializer  # Assuming serializers are in the same app
from .utils.sheet_updater import (
    update_customer_from_sheet,
)  # Assuming sheet_updater is in utils subdir


class CustomerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows customers to be viewed or edited.
    """

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    lookup_field = (
        "did_number"  # <--- ADD THIS LINE: Explicitly use did_number for URL lookups
    )

    # Overriding retrieve to add logging and use get_object()
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a customer using the ViewSet's lookup_field ('did_number').
        """
        # Get the lookup value based on the lookup_field setting
        # self.kwargs contains URL keyword arguments captured by the router
        lookup_url_kwarg = (
            self.lookup_url_kwarg or self.lookup_field
        )  # Usually 'did_number' now
        lookup_value = self.kwargs.get(lookup_url_kwarg)

        print(
            f"Attempting to retrieve customer with lookup_field '{self.lookup_field}' using value='{lookup_value}' from kwarg '{lookup_url_kwarg}'"
        )  # Log lookup attempt

        if not lookup_value:
            print(f"Error: Lookup value not found using kwarg '{lookup_url_kwarg}'!")
            return Response(
                {"detail": "Missing lookup value in request path."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Use the standard get_object() method - it handles lookup based on lookup_field
            instance = self.get_object()
            print(
                f"Successfully retrieved customer via get_object(): {instance}"
            )  # Log success

        except Http404:
            # get_object() raises Http404 if the object is not found
            print(
                f"Customer not found using lookup_field '{self.lookup_field}' with value '{lookup_value}'."
            )  # Log failure
            return Response(
                {"detail": "Customer not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Catch any other unexpected errors during retrieval
            print(
                f"Unexpected error during retrieve for '{lookup_value}': {e}"
            )  # Log other errors
            return Response(
                {"detail": "An error occurred during retrieval."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Serialize and return the data if found
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def update_from_sheet(self, request, pk=None):
        # Note: This action uses the default 'pk' lookup unless lookup_field is changed globally
        # If using lookup_field='did_number', get_object() here will also use 'did_number'
        customer = self.get_object()  # Uses lookup_field='did_number' now
        print(f"Triggering update_from_sheet for: {customer}")
        result = update_customer_from_sheet(customer)

        if result.get("status") == "success":
            return Response(result, status=status.HTTP_200_OK)
        else:
            # Consider returning more specific error codes based on result['error'] if possible
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    @action(detail=False, methods=["post"], url_path="create-or-update-from-sheet")
    def create_or_update_from_sheet(self, request):
        # Extract data from request
        name = request.data.get("name")
        did_number = request.data.get("did_number", "").strip()
        sheet_url = request.data.get("sheet_url")
        print(
            f"Received data: name={name}, did_number={did_number}, sheet_url={sheet_url}"
        )

        # Validate required fields
        if not name or not did_number or not sheet_url:
            return Response(
                {"error": "Fields 'name', 'did_number', and 'sheet_url' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Try to find an existing customer by DID (Primary Key)
        customer = Customer.objects.filter(did_number=did_number).first()
        created = False  # Flag to track if we created a new customer

        if not customer:
            # --- Customer Not Found: Create it ---
            print(f"Customer with DID {did_number} not found. Attempting to create.")
            try:
                # Create the new customer record in the database
                customer = Customer.objects.create(
                    name=name,
                    did_number=did_number,
                    sheet_url=sheet_url,
                    # filetitle will be set later by update_customer_from_sheet if successful
                )
                created = True  # Set flag
                print(f"Successfully created new customer: {customer}")
            except Exception as e:
                # Catch potential errors during creation (like duplicate DID if race condition)
                print(f"Error creating customer with DID {did_number}: {e}")
                # Return a server error if creation fails
                return Response(
                    {"error": f"Failed to create customer: {e}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            # --- End Creation Logic ---
        else:
            # --- Customer Found: Update Name/URL if Changed ---
            print(
                f"Customer with DID {did_number} found. Updating name/URL if changed."
            )
            # Update fields from the request in case they changed
            customer.name = name
            customer.sheet_url = sheet_url
            # Save only these potentially changed fields before triggering sheet update
            customer.save(update_fields=["name", "sheet_url"])

        # --- Process Sheet Data (for both Created and Found customers) ---
        # Now 'customer' is guaranteed to be a valid Customer object (either found or created)
        print(f"Proceeding to update sheet data for: {customer}")
        result = update_customer_from_sheet(customer)  # Call your utility function
        print(f"Result from update_customer_from_sheet: {result}")

        # --- Handle Response ---
        if result.get("status") == "success":
            # Determine appropriate success message and status code
            message = (
                "Customer created and sheet data processed successfully."
                if created
                else "Customer updated and sheet data processed successfully."
            )
            response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK

            return Response(
                {
                    "message": message,
                    "did_number": customer.did_number,  # Good practice to return identifier
                    "spreadsheet_title": result.get("spreadsheet_title"),
                    "records_added": result.get("records_added"),
                },
                status=response_status,  # Use 201 for created, 200 for updated
            )
        else:
            # Sheet processing failed
            error_message = f"Customer {'created' if created else 'found'}, but failed to process sheet: {result.get('error', 'Unknown error')}"
            # Return server error, including details from sheet_updater if available
            # Note: If creation happened but sheet failed, the customer record still exists.
            # You might want more complex logic here later (e.g., delete the created user on sheet failure)
            return Response(
                {"error": error_message, "details": result},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # ... (other methods like retrieve, update_from_sheet) ...
