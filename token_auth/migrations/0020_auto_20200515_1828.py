# Generated by Django 3.0.3 on 2020-05-15 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('token_auth', '0019_auto_20200515_1821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='city',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='education',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='job',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
