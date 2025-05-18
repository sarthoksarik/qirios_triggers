from rest_framework import serializers
from .models import Customer, DemandTitle, Demand, PatientType, Action


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ["description", "dire_text"]


class PatientTypeSerializer(serializers.ModelSerializer):
    # Make 'actions' writable and optional for creation
    actions = ActionSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = PatientType
        fields = ["name", "actions"]


class DemandSerializer(serializers.ModelSerializer):
    # Make 'patient_types' writable and optional
    patient_types = PatientTypeSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = Demand
        fields = ["name", "patient_types"]


class DemandTitleSerializer(serializers.ModelSerializer):
    # Make 'demands' writable and optional
    demands = DemandSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = DemandTitle
        fields = ["title", "demands"]


class CustomerSerializer(serializers.ModelSerializer):
    # Make 'demand_titles' writable and optional
    demand_titles = DemandTitleSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = Customer
        fields = "__all__"  # did_number, name, sheet_url, worksheet_name, filetitle, demand_titles

    def create(self, validated_data):
        # Using .pop("key", []) is robust as it provides a default if the key is not present
        # (which can happen if required=False and the client doesn't send it)
        demand_titles_data = validated_data.pop("demand_titles", [])
        customer = Customer.objects.create(**validated_data)
        for dt_data in demand_titles_data:
            demands_data = dt_data.pop("demands", [])
            demand_title = DemandTitle.objects.create(customer=customer, **dt_data)
            for d_data in demands_data:
                patient_types_data = d_data.pop("patient_types", [])
                demand = Demand.objects.create(demand_title=demand_title, **d_data)
                for pt_data in patient_types_data:
                    actions_data = pt_data.pop("actions", [])
                    patient_type_obj = PatientType.objects.create(
                        demand=demand, **pt_data
                    )
                    for a_data in actions_data:
                        # 'a_data' now directly contains 'description' and 'dire_text'
                        Action.objects.create(patient_type=patient_type_obj, **a_data)
        return customer
