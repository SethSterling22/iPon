from django.urls import path
from register.views import *


from django.conf import settings
from django.conf.urls.static import static

# from .views import published_pons
# from .views import publish_pon

urlpatterns = [
    path('', login_or_signup, name='login'),
    path('main/', main_view, name='main'),
    path('register', logout_user, name='logout'),

    path('published_pons.html/', published_pons, name='published_pons'),
    path('publish_pon.html/', publish_pon, name='publish_pon'),
    path('pon_status.html/', pon_status, name='pon_status'),
    path('previous_pons.html/', previous_pons, name='previous_pons'),
    path('accept_pon/', accept_pon, name="accept_pon"),
    path('update_pon_status/', update_pon_status, name="update_pon_status"),
    path('leave_pon/', leave_pon, name="leave_pon"),
    path('user_profile.html/', user_profile, name="user_profile"),
    path('payment_success/', payment_success, name="payment_success"),
    path('remove_user_after_payments', remover_user_after_payment, name="remover_user_after_payment"),
    path('leave_rating_comment/<int:payment_id>/', leave_rating_comment, name='leave_rating_comment'),

    path('driver/<int:user_id>/', user_form_view, name='user_form'), 
    path('toggle-driver-mode/<int:user_id>/', toggle_driver_mode, name='toggle_driver_mode'),

    # path('', include('django.contrib.auth.urls')),
    # path('', include('login.urls')),
    
]