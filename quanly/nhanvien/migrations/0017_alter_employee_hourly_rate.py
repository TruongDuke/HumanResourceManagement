# Generated by Django 4.2.17 on 2025-01-02 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nhanvien', '0016_employee_hourly_rate_alter_employee_bonus_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='hourly_rate',
            field=models.DecimalField(decimal_places=0, default=50, max_digits=10),
        ),
    ]
