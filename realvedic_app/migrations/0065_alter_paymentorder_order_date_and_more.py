# Generated by Django 4.0.3 on 2023-03-01 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realvedic_app', '0064_alter_paymentorder_order_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentorder',
            name='order_date',
            field=models.TextField(default='2023-03-01 19:05:31.416722+05:30'),
        ),
        migrations.AlterField(
            model_name='user_data',
            name='created_at',
            field=models.TextField(default='2023-03-01 19:05:31.414728+05:30'),
        ),
    ]
