# actionapi/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.http import Http404 # Import Http404
# from django.db import transaction # Consider using transactions later if needed

from .models import Customer # Assuming models are in the same app
from .serializers import CustomerSerializer # Assuming serializers are in the same app
from .utils.sheet_updater import update_customer_from_sheet # Assuming sheet_updater is in utils subdir


class CustomerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows customers to be viewed or edited.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    lookup_field = 'did_number' # <--- ADD THIS LINE: Explicitly use did_number for URL lookups

    # Overriding retrieve to add logging and use get_object()
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a customer using the ViewSet's lookup_field ('did_number').
        """
        # Get the lookup value based on the lookup_field setting
        # self.kwargs contains URL keyword arguments captured by the router
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field # Usually 'did_number' now
        lookup_value = self.kwargs.get(lookup_url_kwarg)

        print(f"Attempting to retrieve customer with lookup_field '{self.lookup_field}' using value='{lookup_value}' from kwarg '{lookup_url_kwarg}'") # Log lookup attempt

        if not lookup_value:
             print(f"Error: Lookup value not found using kwarg '{lookup_url_kwarg}'!")
             return Response({"detail": "Missing lookup value in request path."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Use the standard get_object() method - it handles lookup based on lookup_field
            instance = self.get_object()
            print(f"Successfully retrieved customer via get_object(): {instance}") # Log success

        except Http404:
             # get_object() raises Http404 if the object is not found
             print(f"Customer not found using lookup_field '{self.lookup_field}' with value '{lookup_value}'.") # Log failure
             return Response(
                 {"detail": "Customer not found."}, status=status.HTTP_404_NOT_FOUND
             )
        except Exception as e:
            # Catch any other unexpected errors during retrieval
            print(f"Unexpected error during retrieve for '{lookup_value}': {e}") # Log other errors
            return Response({"detail": "An error occurred during retrieval."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Serialize and return the data if found
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def update_from_sheet(self, request, pk=None):
        # Note: This action uses the default 'pk' lookup unless lookup_field is changed globally
        # If using lookup_field='did_number', get_object() here will also use 'did_number'
        customer = self.get_object() # Uses lookup_field='did_number' now
        print(f"Triggering update_from_sheet for: {customer}")
        result = update_customer_from_sheet(customer)

        if result.get("status") == "success":
            return Response(result, status=status.HTTP_200_OK)
        else:
            # Consider returning more specific error codes based on result['error'] if possible
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Use @transaction.atomic here? Might help if update_customer_from_sheet fails midway
    # @transaction.atomic
    @action(detail=False, methods=["post"], url_path="create-or-update-from-sheet")
    def create_or_update_from_sheet(self, request):
        name = request.data.get("name")
        did_number = request.data.get("did_number", "").strip()
        sheet_url = request.data.get("sheet_url")
        print(
            f"Received data: name={name}, did_number={did_number}, sheet_url={sheet_url}"
        )
        if not name or not sheet_url or not did_number: # Made did_number mandatory here for update logic
            return Response(
                {"error": "Fields 'name', 'did_number', and 'sheet_url' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Try to find existing customer by DID (Primary Key)
        customer = Customer.objects.filter(did_number=did_number).first()

        if not customer:
            # If not found by DID, maybe check by sheet_url as fallback? Or just error?
            # For now, let's assume DID must exist for the update button flow
             # customer = Customer.objects.filter(sheet_url=sheet_url).first() # Optional fallback find
             # Let's handle creation separately if needed, this focuses on update
             print(f"Customer with DID {did_number} not found initially.")
             # Decide if you want this endpoint to *create* if DID not found,
             # or only update existing. Let's stick to update based on flow.
             # If you want create, add Customer.objects.create(...) here.
             # For now, let's assume it finds the customer based on POST test success.
             # If creating: customer = Customer.objects.create(...)

        # Based on previous logs, the customer IS found at this stage in the failing flow
        print(f"Customer found: {customer}") # Should print the customer object if found

        if not customer:
             return Response(
                {"error": f"Customer with DID {did_number} not found. Cannot update."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Update data from sheet (passing the found customer object)
        result = update_customer_from_sheet(customer)
        print(f"Result from update_customer_from_sheet: {result}")

        if result.get("status") == "success":
            # IMPORTANT: Return the DID so frontend *could* potentially use it
            # Although frontend already has it in this flow.
            return Response(
                {
                    "message": "Customer update triggered successfully.",
                    "did_number": customer.did_number, # Return DID
                    "spreadsheet_title": result.get("spreadsheet_title"),
                    "records_added": result.get("records_added"),
                },
                status=status.HTTP_200_OK, # Use 200 OK for successful update trigger
            )
        else:
            # Pass back the error from the sheet updater
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)