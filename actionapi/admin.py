from django.contrib import admin
from .models import Customer, DemandTitle, Demand, PatientType, Action

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('filetitle', 'name', 'did_number')  # Add fields you want to see
# Keep other models registered as-is
admin.site.register(DemandTitle)
admin.site.register(Demand)
admin.site.register(PatientType)
admin.site.register(Action)
