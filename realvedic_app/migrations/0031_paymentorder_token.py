# Generated by Django 4.1.5 on 2023-02-09 04:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realvedic_app', '0030_rename_customer_id_order_data_size_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentorder',
            name='token',
            field=models.TextField(null=True),
        ),
    ]
