from django.db import models


# Main customer model with their DID number and name
class Customer(models.Model):
    did_number = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=255)
    sheet_url = models.URLField(blank=True, null=True)  # New
    worksheet_name = models.CharField(max_length=255, blank=True, null=True)  # New
    filetitle = models.CharField(max_length=255, blank=True)  # <-- New field

    def __str__(self):
        return f"{self.name} ({self.did_number})"


# First category from the sheet
class DemandTitle(models.Model):
    customer = models.ForeignKey(
        Customer, related_name="demand_titles", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)


class Demand(models.Model):
    demand_title = models.ForeignKey(
        DemandTitle, related_name="demands", on_delete=models.CASCADE
    )
    name = models.TextField()


class PatientType(models.Model):
    demand = models.ForeignKey(
        Demand, related_name="patient_types", on_delete=models.CASCADE
    )
    name = models.TextField()


class Action(models.Model):
    patient_type = models.ForeignKey(
        PatientType, related_name="actions", on_delete=models.CASCADE
    )
    description = models.TextField()
