# Generated by Django 5.1.1 on 2024-10-05 00:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nhanvien', '0003_account_user_position'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Account',
        ),
        migrations.RemoveField(
            model_name='user',
            name='position',
        ),
    ]
