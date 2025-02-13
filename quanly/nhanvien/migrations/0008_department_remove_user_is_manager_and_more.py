# Generated by Django 5.1.1 on 2024-10-11 10:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nhanvien', '0007_employee_bonus'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Kế toán', 'Kế toán'), ('Hành chính', 'Hành chính'), ('IT', 'IT'), ('Marketing', 'Marketing')], max_length=100, unique=True)),
                ('code', models.CharField(max_length=10, unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_manager',
        ),
        migrations.AlterField(
            model_name='employee',
            name='department',
            field=models.CharField(choices=[('Kế toán', 'Kế toán'), ('Hành chính', 'Hành chính'), ('IT', 'IT'), ('Marketing', 'Marketing')], max_length=100),
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contract_file', models.FileField(blank=True, null=True, upload_to='contracts/')),
                ('contract_type', models.CharField(max_length=100)),
                ('status', models.CharField(max_length=50)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nhanvien.employee')),
            ],
        ),
    ]
