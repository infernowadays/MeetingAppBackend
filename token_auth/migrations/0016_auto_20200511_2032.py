# Generated by Django 3.0.3 on 2020-05-11 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('token_auth', '0015_auto_20200511_2031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
    ]
