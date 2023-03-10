# Generated by Django 4.0.3 on 2023-03-08 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realvedic_app', '0076_alter_paymentorder_order_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='shipping_price',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='paymentorder',
            name='order_date',
            field=models.TextField(default='2023-03-08 17:41:54.245583+05:30'),
        ),
        migrations.AlterField(
            model_name='user_data',
            name='created_at',
            field=models.TextField(default='2023-03-08 17:41:54.243585+05:30'),
        ),
    ]
