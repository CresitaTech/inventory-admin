from rest_framework import serializers
from .models import OnHandBalanceReport, ProjectedObsolescence, CycleCount

class OnHandBalanceReportSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField()
    allocated = serializers.IntegerField()
    available = serializers.IntegerField()
    # bin = serializers.IntegerField()
    # level = serializers.IntegerField()
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
    location = serializers.SerializerMethodField()
    percentage = serializers.IntegerField()

    class Meta:
        model = CycleCount
        fields = '__all__'  # or list them manually if needed
        read_only_fields = ['accuracy_percentage']
        
    def get_location(self, obj):
        if obj.warehouse.startswith('SF'):
            return 'SSF'
        elif obj.warehouse.startswith('NC'):
            return 'NC'
        return ''

    def get_accuracy_percentage(self, obj):
        try:
            return int(Decimal('100') - obj.percentage)
        except:
            return None
        
from .models import CarryingCost, InventoryOutstanding, PaidInvoices
class CarryingCostSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    damage = serializers.FloatField()
    storage = serializers.FloatField()
    total_inventory_value = serializers.FloatField()
    handling = serializers.FloatField()
    loss = serializers.FloatField()
    

    class Meta:
        model = CarryingCost
        fields = '__all__'  

    def get_location(self, obj):
        if obj.warehouse.startswith('SF'):
            return 'SSF'
        elif obj.warehouse.startswith('NC'):
            return 'NC'
        return ''
    
class InventoryOutstandingSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    

    class Meta:
        model = InventoryOutstanding
        fields = '__all__'  

    def get_location(self, obj):
        if obj.warehouse.startswith('SF'):
            return 'SSF'
        elif obj.warehouse.startswith('NC'):
            return 'NC'
        return ''
    

class PaidInvoicesSerializer(serializers.ModelSerializer):
    total = serializers.FloatField()
    
    class Meta:
        model = PaidInvoices
        fields = '__all__'
        
        
        
from .models import UploadInventoryData

class UploadInventoryDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadInventoryData
        fields = '__all__'