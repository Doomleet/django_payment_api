from rest_framework import serializers

from .models import PaymentProgress, Rate, FlatPayment
from api.serializers import HomeLocationSerializer


class FlatPaymentSerializer(serializers.ModelSerializer):
    flat_number = serializers.CharField(source='flat.flat_number')

    class Meta:
        model = FlatPayment
        fields = [
            'flat_number',
            'water_consumption',
            'water_cost',
            'maintenance_cost',
            'total_cost'
        ]


class PaymentProgressSerializer(serializers.ModelSerializer):
    flat_payments = FlatPaymentSerializer(many=True, read_only=True)
    home = HomeLocationSerializer()

    class Meta:
        model = PaymentProgress
        fields = [
            'task_id',
            'home',
            'month',
            'year',
            'result',
            'status',
            'flat_payments'
        ]


class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = ['rate_type', 'rate']
