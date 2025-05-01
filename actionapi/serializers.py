from rest_framework import serializers
from .models import Customer, DemandTitle, Demand, PatientType, Action


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ["description"]


class PatientTypeSerializer(serializers.ModelSerializer):
    actions = ActionSerializer(many=True)

    class Meta:
        model = PatientType
        fields = ["name", "actions"]


class DemandSerializer(serializers.ModelSerializer):
    patient_types = PatientTypeSerializer(many=True)

    class Meta:
        model = Demand
        fields = ["name", "patient_types"]


class DemandTitleSerializer(serializers.ModelSerializer):
    demands = DemandSerializer(many=True)

    class Meta:
        model = DemandTitle
        fields = ["title", "demands"]


class CustomerSerializer(serializers.ModelSerializer):
    demand_titles = DemandTitleSerializer(many=True)

    class Meta:
        model = Customer
        fields = "__all__"

    def create(self, validated_data):
        demand_titles_data = validated_data.pop("demand_titles")
        customer = Customer.objects.create(**validated_data)
        for dt_data in demand_titles_data:
            demands_data = dt_data.pop("demands")
            demand_title = DemandTitle.objects.create(customer=customer, **dt_data)
            for d_data in demands_data:
                patient_types_data = d_data.pop("patient_types")
                demand = Demand.objects.create(demand_title=demand_title, **d_data)
                for pt_data in patient_types_data:
                    actions_data = pt_data.pop("actions")
                    patient_type_obj = PatientType.objects.create(
                        demand=demand, **pt_data
                    )
                    for a_data in actions_data:
                        Action.objects.create(patient_type=patient_type_obj, **a_data)
        return customer
