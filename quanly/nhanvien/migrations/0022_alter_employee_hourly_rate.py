# Generated by Django 4.2.17 on 2025-01-03 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nhanvien', '0021_alter_employee_late_penalty'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='hourly_rate',
            field=models.DecimalField(decimal_places=0, default=50000, max_digits=10),
        ),
    ]
