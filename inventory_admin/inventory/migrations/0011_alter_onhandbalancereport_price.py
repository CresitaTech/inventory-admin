# Generated by Django 5.2.2 on 2025-06-22 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_alter_onhandbalancereport_bin_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='onhandbalancereport',
            name='price',
            field=models.CharField(max_length=50),
        ),
    ]
