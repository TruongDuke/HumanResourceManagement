# Generated by Django 4.2.17 on 2025-01-02 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nhanvien', '0017_alter_employee_hourly_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='status',
            field=models.CharField(default='Đúng giờ', max_length=20),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='date',
            field=models.DateField(),
        ),
    ]
