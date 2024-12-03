from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import logout
from django.conf import settings

from .Crypt import *

from django.urls import reverse
from functools import wraps

#importing the models from models.py to be used in publish_pon
from .models import Ride
from .models import Location
from .forms import RideForm

#importing google maps for location and the json cause database
import googlemaps
import json
from django.http import JsonResponse
######################## Definición de función login_required ###############################

# Función personalizada de Login_required
def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('user_token'):  
            return HttpResponseRedirect(reverse('login')) 
        return view_func(request, *args, **kwargs)
    return _wrapped_view

######################## Definición de función login_required ###############################

######################## Manejo de usuarios ###############################

# Sacar de la cuenta
@csrf_protect
def logout_user(request):
    if 'user_token' in request.session:
        del request.session['user_token']  # Elimina el ID del usuario de la sesión
    return redirect('login')  # Redirige a la página de login

# Inicio de sesión y registro
@csrf_protect
def login_or_signup(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        #Entrada si el form es de login
        if action == 'login':
            email = request.POST.get('email', None)
            password = request.POST.get('password', None)
            if email and password:
                token = autenticar(email, password)
                if token:
                    request.session['user_token'] = token 
                    return redirect('main')
                else:
                    messages.success(request, ("There was an error in the credentials, please try again."))
                    return redirect('login')

        # Entrada si el form es de registro
        elif action == 'signup':
            form = RegistroForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data.get('Pass')
                password2 = request.POST.get('password2', None)
                if password == password2:
                    # print(form.cleaned_data)
                    
                    # Generar el token con hash del username y el email
                    # username = request.POST.get('Nombre', None)
                    # email = request.POST.get('E_mail', None)
                    # print(form.cleaned_data)
                
                    # Guardar la información del usuario
                    form.save()
                    return redirect('main')  # Redirige a la página de éxito después de guardar el usuario
                else:
                    messages.success(request, ("The passwords doen't match, please ty again."))
                    return redirect('login') 
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.success(request, f"{field}: {error}")
                return redirect('login')
    else:
        form = RegistroForm()
        
    return render(request, 'login.html', {'form': form})

######################## Manejo de usuarios ###############################

#Redirección a la página de main
@csrf_protect
@login_required
def main_view(request):
    context = {
        'google_maps_api_key': settings.GOOGLE_APIK
    }
    return render(request, 'main.html', context)

@login_required
def published_pons(request):
    user_token = request.session.get('user_token')
    if user_token:
        rides = Ride.objects.all()  # Get all rides
        return render(request, 'published_pons.html', {'published_pons': rides})
    else:
        return redirect('login')  # Redirect if user is not authenticated

def create_temp_driver():
    temp_driver = User.objects.create(
        Username='temp_driver',
        E_mail='temp_driver@example.com',  # Provide a valid email
        Is_driver=True,
        Status='temporary',
        License_number='',
        Rate=0.0
    )
    temp_driver.set_password('temp_password')  # Securely set the password
    temp_driver.save()
    return temp_driver
        
@csrf_protect
@login_required
def publish_pon(request):
    user_token = request.session.get('user_token')  # Retrieve user token from the session
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)

            # Extract locations from the data sent from the client
            from_location_name = data.get('from_location')
            to_location_name = data.get('to_location')
            number_of_people = data.get('number_of_people', 1)  # Default to 1 if not provided

            # Validate received locations
            if not from_location_name or not to_location_name:
                return JsonResponse({'error': 'Both from_location and to_location are required.'}, status=400)

            # Geocode to get latitude and longitude
            geocoder = googlemaps.Client(key=settings.GOOGLE_APIK)

            # Get latitude and longitude for start location
            start_geocode = geocoder.geocode(from_location_name)
            if not start_geocode:
                return JsonResponse({'error': f'Could not geocode {from_location_name}'}, status=400)
            start_latitude = start_geocode[0]['geometry']['location']['lat']
            start_longitude = start_geocode[0]['geometry']['location']['lng']

            # Get latitude and longitude for end location
            end_geocode = geocoder.geocode(to_location_name)
            if not end_geocode:
                return JsonResponse({'error': f'Could not geocode {to_location_name}'}, status=400)
            end_latitude = end_geocode[0]['geometry']['location']['lat']
            end_longitude = end_geocode[0]['geometry']['location']['lng']

            # Fetch or create Location instances based on the provided names
            start_location, _ = Location.objects.get_or_create(
                name=from_location_name,
                defaults={'latitude': start_latitude, 'longitude': start_longitude}
            )
            end_location, _ = Location.objects.get_or_create(
                name=to_location_name,
                defaults={'latitude': end_latitude, 'longitude': end_longitude}
            )

            # Create a temporary driver
            temp_driver = create_temp_driver()

            # Now, retrieve the user based on the token
            try:
                user = User.objects.get(token=user_token)  # Assuming token is a field in your User model
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found.'}, status=404)

            # Create a new Ride instance
            ride = Ride(
                Driver=temp_driver,  # Use the temporary driver
                Start_location=start_location,
                End_location=end_location,
                Date_Start=timezone.now(),
                Date_End=timezone.now()
            )
            ride.save()  # Save the Ride instance

            # Optionally, you might want to add passengers if needed
            # Assume user is a passenger
            ride.Passenger.add(user)  # Add the current user as a passenger

            return JsonResponse({'status': 'success'})

    else:
        form = RideForm()
    return render(request, 'publish_pon.html', {'form': form})