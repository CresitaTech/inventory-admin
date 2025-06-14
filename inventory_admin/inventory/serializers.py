from rest_framework import serializers
from .models import OnHandBalanceReport

class OnHandBalanceReportSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField()
    allocated = serializers.IntegerField()
    available = serializers.IntegerField()
    bin = serializers.IntegerField()
    level = serializers.IntegerField()
    price = serializers.FloatField()
    value = serializers.FloatField()

    class Meta:
        model = OnHandBalanceReport
        fields = '__all__'