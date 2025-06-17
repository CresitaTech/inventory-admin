from rest_framework import serializers
from .models import OnHandBalanceReport, ProjectedObsolescence, CycleCount

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
        

class ProjectedObsolescenceSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    price = serializers.FloatField()
    value = serializers.FloatField()
    quantity = serializers.IntegerField()

    class Meta:
        model = ProjectedObsolescence
        fields = '__all__'  

    def get_type(self, obj):
        if obj.warehouse.startswith('SF'):
            return 'SSF'
        elif obj.warehouse.startswith('NC'):
            return 'NC'
        return ''
    
from decimal import Decimal
class CycleCountSerializer(serializers.ModelSerializer):
    accuracy_percentage = serializers.SerializerMethodField()

    class Meta:
        model = CycleCount
        fields = '__all__'  # or list them manually if needed
        read_only_fields = ['accuracy_percentage']

    def get_accuracy_percentage(self, obj):
        try:
            return float(Decimal('100') - obj.percentage)
        except:
            return None