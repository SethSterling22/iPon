from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
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
from django.utils import timezone
from datetime import timedelta

# Become a driver form
from .forms import UserForm

# Importing model Payment for previous_pons
from .models import Payment

# Importing Rating form
from .forms import RatingCommentForm

#stripe payment management
import stripe
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
stripe.api_key = settings.STRIPE_SK
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
                username = get_username(email)
                if token:
                    request.session['user_token'] = token 
                    if username:
                        username = clean_username(username)
                    # Almacena en la sesión
                    request.session['username'] = username
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
    username = request.session.get('username')  

    user_token = request.session.get('user_token')
    if user_token:
        try:
            # Retrieve the user based on the token
            user = User.objects.get(Token=user_token)

            # if user.Is_driver:
            #     payments = Payment.objects.filter(Driver__ID_U=user.ID_U)  # Assuming Driver is a foreign key in Payment
            #     # Calculate average rating
            #     if payments.exists():
            #         total_rating = sum(payment.Rate for payment in payments if payment.Rate is not None)
            #         average_rating = total_rating / payments.count()
            #     else:
            #         average_rating = 0  # Default to 0 if no ratings exist
            # else:
            #     average_rating = None  # No average rating for non-drivers

            # Prepare context data to send to the template
            context = {
                'user_id': user.ID_U,
                'username': user.Username,
                'is_driver': user.Is_driver,
                'actual_pon': user.Actual_Pon,
                # 'average_rating': round(average_rating, 2) if average_rating is not None else None,  # Round to 2 decimal places
                'is_active': user.Is_active if user.Is_driver else None,
                'rate': user.Rate if user.Is_driver else None,
                'google_maps_api_key': settings.GOOGLE_APIK,
            }
            return render(request, 'main.html', context)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('login') 
    else:
        context = {
            'username': username, 
            'google_maps_api_key': settings.GOOGLE_APIK
        }
        return render(request, 'main.html', context)


@login_required
def toggle_driver_mode(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, ID_U=user_id)
        
        # Alternar el estado de Is_active
        user.Is_active = not user.Is_active  # Cambia a True si es False, y viceversa
        user.save()
        
        return redirect('main')  # Redirige a la vista principal
    return redirect('main')  # Redirigir en caso de error


@login_required
def published_pons(request):
    user_token = request.session.get('user_token')
    if user_token:
        rides = Ride.objects.exclude(Status='Paid')  # Exclude rides with status 'Paid'
        user = User.objects.get(Token=user_token)

        # Prepare context data to send to the template
        context = {
            'is_active': user.Is_active if user.Is_driver else None,
            'published_pons': rides,
        }

        return render(request, 'published_pons.html', context)
    else:
        return redirect('login')  # Redirect if user is not authenticated

@csrf_protect
@login_required
def pon_status(request):
    user_token = request.session.get('user_token')
    if user_token:
        try:
            # get the user object using the toke
            user = User.objects.get(Token=user_token)

            # query the most recent active ride where the user is a passenger
            recent_ride = user.Actual_Pon
            occupied_seats = recent_ride.Passenger.count() if recent_ride else 0

            # if not recent_ride:
            #     return JsonResponse({'status': 'error', 'message': 'Ride not found.'}, status=404)

            return render(request, 'pon_status.html', {'recent_ride': recent_ride, 'occupied_seats': occupied_seats, 'is_active': user.Is_active if user.Is_driver else None})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
    else:
        return redirect('login')  # Redirect if user is not authenticated


@login_required
def previous_pons(request):
    user_token = request.session.get('user_token')
    if user_token:
        user = get_object_or_404(User, Token=user_token)  # Use get_object_or_404 for safety
        
        # Fetch payments related to the user
        if user.Is_active:
            payments = Payment.objects.filter(Driver=user)
        else:
            payments = Payment.objects.filter(Passenger=user)

        return render(request, 'previous_pons.html', {
            'previous_payments': payments,
            'is_active': user.Is_active,
            'user_id': user.ID_U  # Pass the user ID to the template
        })
    else:
        return redirect('login')  # Redirect if user is not authenticated


def create_temp_driver():
    # Create or get the existing temporary driver
    temp_driver, created = User.objects.get_or_create(
        E_mail='temp_driver@example.com',  # Use a known email
        defaults={
            'Username': 'temp_driver',
            'Is_driver': True,
            'Status': 'temporary',
            'License_number': '',
            'Rate': 0.0
        }
    )
    
    if created:
        temp_driver.set_password('temp_password')  # Set password only if created
        temp_driver.save()
    
    return temp_driver


@csrf_protect
@login_required
def publish_pon(request):
    user_token = request.session.get('user_token')  # Retrieve user token from the session
    
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)

            from_location_name = data.get('from_location')
            to_location_name = data.get('to_location')
            number_of_people = data.get('number_of_people', 1)  # Default to 1

            if not from_location_name or not to_location_name:
                return JsonResponse({'error': 'Both from_location and to_location are required.'}, status=400)

            # Geocode locations
            geocoder = googlemaps.Client(key=settings.GOOGLE_APIK)
            start_geocode = geocoder.geocode(from_location_name)
            end_geocode = geocoder.geocode(to_location_name)

            if not start_geocode or not end_geocode:
                return JsonResponse({'error': 'Could not geocode the provided locations.'}, status=400)

            start_latitude = start_geocode[0]['geometry']['location']['lat']
            start_longitude = start_geocode[0]['geometry']['location']['lng']
            end_latitude = end_geocode[0]['geometry']['location']['lat']
            end_longitude = end_geocode[0]['geometry']['location']['lng']

            start_location, _ = Location.objects.get_or_create(
                name=from_location_name,
                defaults={'latitude': start_latitude, 'longitude': start_longitude}
            )
            end_location, _ = Location.objects.get_or_create(
                name=to_location_name,
                defaults={'latitude': end_latitude, 'longitude': end_longitude}
            )

            # Retrieve the user based on the token
            if user_token:
                try:
                    user = User.objects.get(Token=user_token)
                except User.DoesNotExist:
                    return JsonResponse({'error': 'User not found.'}, status=404)
            else:
                return JsonResponse({'error': 'User token is missing.'}, status=401)

            # Check if the user already has an active ride
            if user.Actual_Pon:
                return JsonResponse({'error': 'You already have an active ride.'}, status=400)

            # Retrieve or create the temporary driver
            temp_driver = create_temp_driver()

            # Create a new Ride instance using the temporary driver
            ride = Ride(
                Driver=temp_driver,
                Start_location=start_location,
                End_location=end_location,
                Date_Start=timezone.now(),
                Date_End=timezone.now() + timedelta(minutes=15),  # Set end time 15 minutes in the future
                Status='Waiting'  # Set the initial status
            )
            ride.save()  # Save the Ride instance first

            # Add the user as a passenger
            ride.Passenger.add(user)  # Use the add() method for ManyToManyField
            
            # Update the user's Actual_Pon to the new ride
            user.Actual_Pon = ride
            user.save()

            return JsonResponse({'status': 'success'})
    
    return JsonResponse({'error': 'Invalid request method or content type'}, status=400)

@login_required
def accept_pon(request):
    user_token = request.session.get('user_token')  # Retrieve user token from the session
    if request.method == 'POST':
        try:
            # get the pon id from the request
            pon_id = request.POST.get('pon_id')

            if not pon_id:
                return JsonResponse({'status': 'error', 'message': 'Pon ID is required.'}, status=400)

            # retrieve the logged-in user
            user = User.objects.get(Token=user_token)
            # print(f"user: {user.E_mail}")

            # check if the user already has an active ride
            if user.Actual_Pon and user.Actual_Pon.Status in ['Waiting', 'In Progress']:
                return JsonResponse({'status': 'error', 'message': 'You already have an active ride. Finish it before accepting a new one.'}, status=403)

            # fetch the ride from DB
            ride = get_object_or_404(Ride, Ride_id=pon_id)

            # Check if the user is currently a driver
            if user.Is_active: # Is active being what checks if the user is currently a driver
                # If the ride's current driver is temp_driver the placeholder, replace them with the new driver
                if ride.Driver.Username == 'temp_driver' or ride.Driver.Username == user.Username:
                    ride.Driver = user  # Assign the new driver
                    ride.save()
                    user.Actual_Pon = ride
                    user.save()
                    return JsonResponse({'status': 'success', 'message': 'You have successfully accepted this Pon as the driver.'})

                # If the ride already has a driver, return an error
                return JsonResponse({'status': 'error', 'message': 'This ride already has a driver.'}, status=403)

            # check if the ride is full
            passenger_count = ride.Passenger.count()
            if passenger_count >= 4:
                return JsonResponse({'status': 'error', 'message': 'This ride is already full. Please choose another ride.'}, status=403)

            # add the user as a passenger to the ride
            #if user in ride.Passenger.all():
                #return JsonResponse({'status': 'error', 'message': 'You are already a passenger in this ride.'}, status=400)
            
            ride.Passenger.add(user)
            ride.save()

            # update the user's actual pon id to reference this ride
            user.Actual_Pon = ride
            user.save()
            return JsonResponse({'status': 'success', 'message': 'You have successfully accepted this Pon.'})
        except Ride.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Ride not found.'}, status=404)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
        except Exception as e:
            # print(f"Error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})




# @csrf_protect
# @login_required
# def update_pon_status(request):
#     if request.method == 'POST':
#         try:
#             body = json.loads(request.body)
#             ride_id = body.get('ride_id')  # fetch ride_id from JSON

#             if not ride_id:
#                 return JsonResponse({'status': 'error', 'message': 'Ride ID is required.'}, status=400)
            
#             ride = Ride.objects.get(Ride_id=ride_id)  # get the ride that will be updated

#             user_token = request.session.get('user_token')  # Retrieve user token from the session
#             user = User.objects.get(Token=user_token)

#             if user not in ride.Passenger.all():
#                 return JsonResponse({'status': 'error', 'message': 'User  is not a passenger in this ride.'}, status=403)

#             # Update the status
#             if ride.Status == 'Waiting':
#                 ride.Status = 'In Progress'
#             elif ride.Status == 'In Progress':
#                 ride.Status = 'Finished'
#                 ride.save()

#                 # Create a Stripe Checkout session for each passenger
                
#                 session = stripe.checkout.Session.create(
#                     payment_method_types=['card'],
#                     line_items=[
#                         {
#                             'price_data': {
#                                 'currency': 'usd',
#                                 'product_data': {
#                                     'name': f"Payment for Ride #{ride.Ride_id}",
#                                 },
#                                 'unit_amount': 1000,  # Ride cost in cents
#                             },
#                             'quantity': 1,
#                         },
#                     ],
#                     mode='payment',
#                     success_url='https://aery.stegosaurus-panga.ts.net/payment_success/',
#                 )
#                 ride_instance = Ride.objects.get(Ride_id=ride.Ride_id)

#                 # Create a Payment record for each passenger
#                 payment = Payment(
#                     Passenger=user,
#                     Driver=ride.Driver,
#                     amount=10,
#                     Pon_id=ride_instance,
#                     comment='Payment for the completed ride.',
#                     Rate=0.0  # initial rating
#                 )
#                 payment.save()

#                 return JsonResponse({'status': 'success', 'message': 'Ride status updated to Finished. Redirecting to payment.'})
            
#             ride.save()
#             return JsonResponse({'status': 'success', 'message': 'Ride status updated successfully.'})
            
#         except Ride.DoesNotExist:
#             return JsonResponse({'status': 'error', 'message': 'Ride not found.'}, status=404)
#         except User.DoesNotExist:
#             return JsonResponse({'status': 'error', 'message': 'User  not found.'}, status=404)
#         except Exception as e:
#             return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

#     return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)




@csrf_protect
@login_required
def update_pon_status(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            ride_id = body.get('ride_id')  # fetch ride_id from JSON
            print(f"Ride_id: {ride_id}")

            if not ride_id:
                return JsonResponse({'status': 'error', 'message': 'Ride ID is required.'}, status=400)
            
            ride = Ride.objects.get(Ride_id=ride_id) # get the ride that will be updated

            user_token = request.session.get('user_token')  # Retrieve user token from the session
            user = User.objects.get(Token=user_token)

            if user not in ride.Passenger.all():
                return JsonResponse({'status': 'error', 'message': 'User is not a passenger in this ride.'}, status=403)

            # update the status
            if ride.Status == 'Waiting':
                ride.Status = 'In Progress'
            elif ride.Status == 'In Progress':
                ride.Status = 'Finished'
                ride.save()

                # Create a Stripe Checkout session
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[
                        {
                            'price_data': {
                                'currency': 'usd',
                                'product_data': {
                                    'name': f"Payment for Ride #{ride.Ride_id}",
                                },
                                'unit_amount': 1000,  # Ride cost in cents
                            },
                            'quantity': 1,
                        },
                    ],
                    mode='payment',
                    success_url='https://aery.stegosaurus-panga.ts.net/payment_success/',
                    
                )

                ride_instance = Ride.objects.get(Ride_id=ride.Ride_id)
                # Create a Payment record for each passenger
                payment = Payment(
                    Passenger=user,
                    Driver=ride.Driver,
                    amount=10,
                    Pon_id=ride_instance,
                    comment='Payment for the completed ride.',
                    Rate=0.0  # initial rating
                )
                payment.save()

                return JsonResponse({
                    'status': 'success',
                    'message': 'Ride status updated to Finished. Redirecting to payment.',
                    'redirect_url': session.url
                })

            ride.save()
            return JsonResponse({'status': 'success', 'message': 'Ride status updated successfully.'})
            
        except Ride.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Ride not found.'}, status=404)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)







@csrf_protect
@login_required
def user_profile(request):
    user_token = request.session.get('user_token')
    if user_token:
        try:
            # Retrieve the user based on the token
            user = get_object_or_404(User, Token=user_token)
            # Fetch payments related to the user if they are a driver
            if user.Is_driver:
                payments = Payment.objects.filter(Driver__ID_U=user.ID_U)  # Assuming Driver is a foreign key in Payment
                # Calculate average rating
                if payments.exists():
                    total_rating = sum(payment.Rate for payment in payments if payment.Rate is not None)
                    average_rating = total_rating / payments.count()
                    # Update the user's Rate with the average rating
                    user.Rate = round(average_rating, 2)  # Round to 2 decimal places
                    user.save()  # Save the updated rating to the user model

                else:
                    average_rating = 0  # Default to 0 if no ratings exist
                    user.save()
            else:
                average_rating = None  # No average rating for non-drivers
            # Prepare context data to send to the template
            context = {
                'username': user.Username,
                'email': user.E_mail,
                'is_driver': user.Is_driver,
                'phone_number': user.Phone_number,  # Add phone number
                'license_number': user.License_number if user.Is_driver else None,  # License number for drivers
                'average_rating': round(user.Rate, 2) if user.Is_driver else None,  # Round to 2 decimal places
                'Is_active': user.Is_active if user.Is_driver else None,
                'Car_Model': user.Car_Model if user.Is_driver else None,
                'Car_Brand': user.Car_Brand if user.Is_driver else None,
                'Car_Year': user.Car_Year if user.Is_driver else None,
                'License_plate': user.License_plate if user.Is_driver else None,
            }
            return render(request, 'user_profile.html', context)
        except User.DoesNotExist:
            messages.error(request, "User  not found.")
            return redirect('main')  # Redirect if user is not found
    else:
        return redirect('main')  # Redirect if user is not authenticated

        
@login_required
def leave_pon(request):
    user_token = request.session.get('user_token') # retrieve user token from session
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            pon_id = body.get('pon_id')
            # print(f"Pon_id: {pon_id}")

            if not pon_id:
                return JsonResponse({'status': 'error', 'message': 'Pon ID is required.'}, status=400)
            
            # retrieve the logged in user
            user = User.objects.get(Token=user_token)

            # fetch the ride from the DB
            ride = get_object_or_404(Ride, Ride_id=pon_id)

            # ensure the user is actually a passenger in the ride
            if not (user in ride.Passenger.all() or user == ride.Driver):
                return JsonResponse({'status': 'error', 'message': 'You are not a passenger in this ride.'}, status=403)
            
            # check the ride status so user's cant leave mid ride to avoid paying
            # if ride.Status != 'Waiting':
            if ride.Status == 'In Progress':
                return JsonResponse({
                    'status': 'error',
                    'message': 'You cannot leave this ride as it is already in progress.'
                }, status=403)
            
            if user == ride.Driver:
                if user.Is_active:  # Check if the driver is active
                    temp_driver = create_temp_driver()  # Create a temporary driver
                    ride.Driver = temp_driver  # Assign the temporary driver to the ride
                    ride.save()  # Save the updated ride
            else:
                # remove the user from the ride's passenger list
                ride.Passenger.remove(user)
                ride.save()

            # set the user's current ride to null
            user.Actual_Pon = None
            user.save()

            return JsonResponse({'status': 'success', 'message': 'You have successfully left the ride.'})
        except Ride.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Ride not found.'}, status=404)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

@csrf_protect
@login_required
def payment_success(request):
    user_token = request.session.get('user_token')  # Retrieve user token from session

    try:
        # Retrieve the logged-in user
        user = User.objects.get(Token=user_token)

        # Ensure the user has an active ride
        if not user.Actual_Pon:
            return JsonResponse({'status': 'error', 'message': 'No active ride found for the user.'}, status=404)

        # Fetch the active ride
        ride = user.Actual_Pon

        # Update the ride's status to "Paid"
        ride.Status = "Paid"
        ride.save()

        # Remove the user from the ride's passenger list
        ride.Passenger.remove(user)

        # Set the user's Actual_Pon field to null
        user.Actual_Pon = None
        user.save()

        # Redirect to the user's Pon Status page or main page
        return redirect('main')

    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User  not found.'}, status=404)
    except Ride.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Ride not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def remover_user_after_payment(request):
    # remove the user from a ride after they have paid
    # this is triggered when a user is redirected to their pon_status after payment
    user_token = request.session.get('user_token')  # Retrieve user token from session

    try:
        # Retrieve the logged-in user
        user = User.objects.get(Token=user_token)

        # Ensure the user has an active ride
        if not user.Actual_Pon:
            return JsonResponse({'status': 'error', 'message': 'No active ride found for the user.'}, status=404)

        # Fetch the active ride
        ride = user.Actual_Pon

        # Update the ride's status to "Paid"
        ride.Status = "Paid"
        ride.save()

        # Remove the user from the ride's passenger list
        ride.Passenger.remove(user)

        # Set the user's Actual_Pon field to null
        user.Actual_Pon = None
        user.save()

        # Redirect to the user's Pon Status page
        return redirect('main')

    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
    except Ride.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Ride not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# Become a driver
def user_form_view(request, user_id):
    user_token = request.session.get('user_token')
    # user = get_object_or_404(User, ID_U=request.user.ID_U) 
    user = User.objects.get(Token=user_token)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)  # Pasar la instancia del usuario
        if form.is_valid():
            user.Is_driver = True
            form.save()  # Guardar los cambios en el usuario existente
            return redirect('main')  # Redirigir a la página de éxito
    else:
        form = UserForm(instance=user)  # Cargar el formulario con datos del usuario
        user.Is_driver = True 
    
    return render(request, 'driver.html', {'form': form, 'user': user})

@login_required

@login_required
def leave_rating_comment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    user_token = request.session.get('user_token')
    user = get_object_or_404(User, Token=user_token)  # Use get_object_or_404 for safety
    if request.method == 'POST':
        # Check if the current user is the passenger for this payment
        if payment.Passenger.ID_U != user.ID_U:
            return JsonResponse({'status': 'error', 'message': 'You cannot rate this ride.'}, status=403)
        
        # Check if the review has already been submitted
        if payment.comment != "Payment for the completed ride.":
            return JsonResponse({'status': 'error', 'message': 'You cannot edit this comment anymore.'}, status=403)


        # Create a form instance with the submitted data
        form = RatingCommentForm(request.POST)
        
        if form.is_valid():
            # Update the payment instance with the new rating and comment
            payment.Rate = form.cleaned_data['Rate']
            payment.comment = form.cleaned_data['comment']
            payment.save()  # Save the rating and comment to the Payment instance
            
            return JsonResponse({'status': 'success', 'message': 'Rating and comment submitted successfully.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form submission.'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)