# Generated by Django 5.1 on 2024-12-02 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0003_alter_ride_driver'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ride',
            name='Passenger',
        ),
        migrations.AddField(
            model_name='ride',
            name='Passenger',
            field=models.ManyToManyField(related_name='rides_as_passenger', to='register.user'),
        ),
    ]
