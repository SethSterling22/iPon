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
    # path('', include('django.contrib.auth.urls')),
    # path('', include('login.urls')),
    
]