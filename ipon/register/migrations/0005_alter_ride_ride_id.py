# Generated by Django 5.1 on 2024-12-03 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0004_remove_ride_passenger_ride_passenger'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ride',
            name='Ride_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]