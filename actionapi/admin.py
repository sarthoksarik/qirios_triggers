from django.contrib import admin
from .models import Customer, DemandTitle, Demand, PatientType, Action

admin.site.register(Customer)
admin.site.register(DemandTitle)
admin.site.register(Demand)
admin.site.register(PatientType)
admin.site.register(Action)
