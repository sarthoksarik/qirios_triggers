# actionapi/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet

router = DefaultRouter()
# This registers /api/customers/ and /api/customers/{pk}/ etc.
router.register(r"customers", CustomerViewSet, basename='customer') # Added basename for clarity

urlpatterns = [
    # Only include the router-generated URLs
    path("", include(router.urls)),
    # Comment out or remove the explicit path below:
    # path("customer/<str:did_number>/", CustomerViewSet.as_view({"get": "retrieve"})),
]