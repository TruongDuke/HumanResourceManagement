# Generated by Django 4.2.17 on 2025-01-03 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nhanvien', '0018_attendance_status_alter_attendance_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='late_penalty',
            field=models.DecimalField(decimal_places=0, default=20, max_digits=10),
        ),
    ]
