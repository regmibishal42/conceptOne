# Generated by Django 2.2.12 on 2021-05-24 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_auto_20210520_0605'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='amount',
            field=models.IntegerField(default=0, max_length=100),
        ),
    ]
