# Generated by Django 5.1.3 on 2024-12-12 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nhanvien', '0014_task'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
