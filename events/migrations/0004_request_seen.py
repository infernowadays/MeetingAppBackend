# Generated by Django 3.0.3 on 2020-04-20 23:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_auto_20200419_2044'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='seen',
            field=models.BooleanField(default=False),
        ),
    ]
