# actionapi/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomerViewSet

router = DefaultRouter()
# This registers /api/customers/ and /api/customers/{pk}/ etc.
router.register(
    r"customers", CustomerViewSet, basename="customer"
)  # Added basename for clarity

urlpatterns = [
    # Only include the router-generated URLs
    path("", include(router.urls)),
]
