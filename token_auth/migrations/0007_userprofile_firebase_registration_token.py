# Generated by Django 3.0.3 on 2020-04-28 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('token_auth', '0006_auto_20200427_2025'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='firebase_registration_token',
            field=models.TextField(blank=True, max_length=256),
        ),
    ]
