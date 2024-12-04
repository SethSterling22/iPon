from django.urls import path
from . import views
from register import views

urlpatterns = [
    path('map/', views.map_view, name='map'),
    path('register/', logout_user, name='logout'),

    path('published_pons.html/', published_pons, name='published_pons'),
    path('publish_pon.html/', publish_pon, name='publish_pon'),
    path('pon_status.html/', pon_status, name='pon_status'),
    path('previous_pons.html/', previous_pons, name='previous_pons'),
    # path('register/', include('register.urls')),
]
