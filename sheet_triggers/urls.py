from django.urls import path
from .views import run_script, run_script_sms

urlpatterns = [
    path('run-script/', run_script),
    path('run-smsscript/', run_script_sms),
]