# Generated by Django 3.0.3 on 2020-05-15 18:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('token_auth', '0022_auto_20200515_2123'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='categories',
        ),
    ]
