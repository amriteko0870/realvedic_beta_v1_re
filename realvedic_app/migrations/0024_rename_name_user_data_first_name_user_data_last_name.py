# Generated by Django 4.1.5 on 2023-02-03 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realvedic_app', '0023_user_address_user_cart_user_data'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user_data',
            old_name='name',
            new_name='first_name',
        ),
        migrations.AddField(
            model_name='user_data',
            name='last_name',
            field=models.TextField(blank=True),
        ),
    ]
