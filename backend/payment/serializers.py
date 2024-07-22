from rest_framework import serializers

from .models import PaymentProgress, Rate


class PaymentProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProgress
        fields = [
            'home',
            'street',
            'month',
            'year',
            'result',
            'status',
            'task_id'
        ]


class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = ['rate_type', 'rate']
