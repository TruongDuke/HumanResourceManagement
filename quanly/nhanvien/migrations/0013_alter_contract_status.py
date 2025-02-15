# Generated by Django 5.1.3 on 2024-11-18 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nhanvien', '0012_remove_contract_contract_file_contract_approval_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='status',
            field=models.CharField(choices=[('Active', 'Còn hạn'), ('Expired', 'Hết hạn'), ('Renewed', 'Đã gia hạn'), ('Terminated', 'Đã kết thúc')], default='Active', max_length=50),
        ),
    ]
