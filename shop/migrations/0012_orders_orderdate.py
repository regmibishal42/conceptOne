# Generated by Django 2.2.12 on 2021-06-20 13:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_auto_20210619_0804'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='orderDate',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
