# Generated by Django 3.0.3 on 2020-04-18 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20200413_1753'),
        ('token_auth', '0003_remove_userprofile_firebase_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='categories',
            field=models.ManyToManyField(blank=True, related_name='profiles', to='events.Category'),
        ),
    ]