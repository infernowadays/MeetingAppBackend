# Generated by Django 3.0.3 on 2020-05-28 15:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email_service', '0002_auto_20200528_1857'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='confirmationcode',
            unique_together=set(),
        ),
    ]
