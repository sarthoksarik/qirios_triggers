from django.urls import path
from .views import run_script

urlpatterns = [
    path('run-script/', run_script),
]