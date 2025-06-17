from django.db import models

# Create your models here.

class OnHandBalanceReport(models.Model):
    item_number = models.TextField()
    location = models.CharField(max_length=50)
    warehouse = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    currency = models.CharField(max_length=20)
    Commodity = models.CharField(max_length=200)
    name = models.TextField()
    gl_acount =  models.DecimalField(max_digits=15, decimal_places=0)
    storage_on_hand = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=0)
    allocated = models.DecimalField(max_digits=10, decimal_places=0)
    available = models.DecimalField(max_digits=10, decimal_places=0)
    uom = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=19, decimal_places=6)
    value = models.DecimalField(max_digits=19, decimal_places=6)
    aisle = models.CharField(max_length=20)
    bin = models.DecimalField(max_digits=19, decimal_places=0)
    level = models.DecimalField(max_digits=10, decimal_places=0)
    created_by = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    
    class Meta:
        db_table = 'onhand_balances'
        verbose_name = "Onhand Balance"
        verbose_name_plural = 'Onhand Balances'




class ProjectedObsolescence(models.Model):
    warehouse = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    item_number = models.TextField()
    item_name = models.CharField(max_length=255)
    lot_number = models.CharField(max_length=100)
    expiration_date = models.CharField(max_length=20)
    quantity = models.DecimalField(max_digits=10, decimal_places=0)
    uom = models.CharField(max_length=20)  # UOM = Unit of Measure
    price = models.DecimalField(max_digits=19, decimal_places=6)
    value = models.DecimalField(max_digits=19, decimal_places=6)

    # def __str__(self):
    #     return f"{self.item_name} - {self.lot_number}"
    
        
    class Meta:
        db_table = 'projected_obsolescence'
        verbose_name = "Projected Obsolescence"
        verbose_name_plural = 'Projected Obsolescences'