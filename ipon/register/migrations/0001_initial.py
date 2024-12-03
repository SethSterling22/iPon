# Generated by Django 5.1 on 2024-11-27 19:45

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('ID_U', models.AutoField(primary_key=True, serialize=False)),
                ('E_mail', models.CharField(max_length=69, unique=True)),
                ('Username', models.CharField(max_length=50)),
                ('Pass', models.CharField(max_length=128)),
                ('Token', models.TextField()),
                ('Phone_number', models.CharField(max_length=20)),
                ('Is_driver', models.BooleanField(default=False, help_text='Indica si el usuario es conductor.')),
                ('Status', models.CharField(max_length=20)),
                ('License_number', models.CharField(max_length=50)),
                ('Rate', models.FloatField(default=0.0, help_text='Rating of the driver from 0.0 to 5.0')),
            ],
        ),
        migrations.CreateModel(
            name='Ride',
            fields=[
                ('Ride_id', models.AutoField(default=1, primary_key=True, serialize=False)),
                ('Date_Start', models.DateTimeField(default=django.utils.timezone.now)),
                ('Date_End', models.DateTimeField(default=django.utils.timezone.now)),
                ('End_location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='end_rides', to='register.location')),
                ('Start_location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='start_rides', to='register.location')),
                ('Driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rides_as_driver', to='register.user')),
                ('Passenger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rides_as_passenger', to='register.user')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('Date', models.DateTimeField(auto_now_add=True)),
                ('Pon_id', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='register.ride')),
                ('Driver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receive_payment', to='register.user')),
                ('Passenger', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='makes_payment', to='register.user')),
            ],
        ),
    ]
