from django.db import models
from datetime import timedelta
from django.utils import timezone

###########################################################################################################
# Modelo del usuario
class User(models.Model):
    ID_U = models.AutoField(primary_key=True)
    E_mail = models.CharField(max_length=69, unique=True)
    Username = models.CharField(max_length=50)
    Pass = models.CharField(max_length=128)
    Token = models.TextField()
    Phone_number = models.CharField(max_length=20)
    Actual_Pon = models.ForeignKey('Ride', null=True, related_name='Actual_pon', on_delete=models.CASCADE)

    Is_active = models.BooleanField(default=False, help_text="Indica si el conductor está activo.")
    Is_driver = models.BooleanField(default=False, help_text="Indica si el usuario es conductor.")
    Car_Brand = models.CharField(max_length=20, null=True, blank=True)
    Car_Model = models.CharField(max_length=20, null=True, blank=True)
    License_plate = models.CharField(max_length=20, null=True, blank=True)
    Car_Year = models.CharField(max_length=20, null=True, blank=True)
    License_number = models.CharField(max_length=50)
    Rate = models.FloatField(default=0.0, help_text="Rating of the driver from 0.0 to 5.0")

###########################################################################################################
# Moodelo de Pon
class Ride(models.Model):
    STATUS_CHOICES = [
        ('Waiting', 'Waiting'),
        ('In Progress', 'In Progress'),
        ('Finished', 'Finished'),
        ('Paid', 'Paid'),
    ]
    Ride_id = models.AutoField(primary_key=True)
    Driver = models.ForeignKey(User, related_name='rides_as_driver', on_delete=models.CASCADE)
    Passenger = models.ManyToManyField(User, related_name='rides_as_passenger')
    Start_location = models.ForeignKey('Location', related_name='start_rides', on_delete=models.CASCADE)
    End_location = models.ForeignKey('Location', related_name='end_rides', on_delete=models.CASCADE)
    Date_Start = models.DateTimeField(default=timezone.now)
    Date_End = models.DateTimeField(blank=True, null=True)
    Status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Waiting",

    )

    def save(self, *args, **kwargs):
        # Establecer Date_End como una hora después de Date_Start
        if self.Date_Start:
            self.Date_End = self.Date_Start + timedelta(hours=1)
        super().save(*args, **kwargs)

###########################################################################################################
# Modelo de pagos
class Payment(models.Model):
    Passenger = models.ForeignKey(User, related_name='payments_as_passenger', null=True, blank=True, on_delete=models.CASCADE)
    Driver = models.ForeignKey(User, related_name='payments_as_driver', null=True, blank=True, on_delete=models.CASCADE) 
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    Date = models.DateTimeField(auto_now_add=True)
    Pon_id = models.ForeignKey(Ride, on_delete=models.CASCADE, null=True, default=1)
    
    comment = models.TextField(blank=True, null=True)
    Rate = models.FloatField(default=0.0, help_text="Rating of the driver from 0.0 to 5.0")

###########################################################################################################
# Modelo de locación
class Location(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

