# Generated by Django 4.0.3 on 2022-03-16 04:08

import authentication.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userauthentication',
            name='token',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='userauthentication',
            name='token_expired',
            field=models.DateTimeField(blank=True, default=authentication.models.expire),
        ),
    ]
