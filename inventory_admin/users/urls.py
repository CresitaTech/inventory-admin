from django.contrib import admin
from django.urls import path, include
# from rest_framework import routers
# from rest_framework.authtoken.views import obtain_auth_token

from users.views import login_view, signup_view, fetch_nc_view, fetch_sf_view
# from users.authentication import CustomAuthToken

# router = routers.DefaultRouter()

urlpatterns = [
    # path('', include(router.urls)),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='login'),
    path('fetch_sf_report/', fetch_sf_view, name='sf'),
    path('fetch_nc_report/', fetch_nc_view, name='nc'),
    # path('register/', views.register_view, name='register'),
    # Add more paths as needed
]