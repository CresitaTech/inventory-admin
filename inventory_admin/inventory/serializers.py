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
        
        

from rest_framework import serializers
from .models import ProjectedObsolescence

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
            return 'SF'
        elif obj.warehouse.startswith('NC'):
            return 'NC'
        return ''