# Generated by Django 3.0.3 on 2020-05-14 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('token_auth', '0016_auto_20200511_2032'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_stuff',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_superuser',
            field=models.BooleanField(default=False),
        ),
    ]
