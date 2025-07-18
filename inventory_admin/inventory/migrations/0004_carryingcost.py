# Generated by Django 5.2.2 on 2025-06-20 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_rename_price_cyclecount_cycle_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarryingCost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cycle_count', models.DecimalField(decimal_places=0, max_digits=19)),
                ('warehouse', models.CharField(max_length=100)),
                ('Storage', models.DecimalField(decimal_places=4, max_digits=19)),
                ('total_inventory_value', models.DecimalField(decimal_places=4, max_digits=19)),
                ('date', models.CharField(max_length=20)),
                ('Handling', models.DecimalField(decimal_places=0, max_digits=19)),
                ('Loss', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('Damage', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
            ],
            options={
                'verbose_name': 'Carrying Cost',
                'verbose_name_plural': 'Carrying Costs',
                'db_table': 'carrying_cost',
            },
        ),
    ]
