# Generated by Django 3.0.3 on 2020-04-19 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
        ('token_auth', '0004_userprofile_categories'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='categories',
            field=models.ManyToManyField(blank=True, related_name='profiles', to='common.Category'),
        ),
    ]