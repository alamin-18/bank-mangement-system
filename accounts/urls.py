from django.urls import path
from .views import UserRegistationsForms,UserBankAccountUpdate

urlpatterns = [
   
    path('register/', UserRegistationsForms.as_view(),name='register'),
    path('profile/', UserBankAccountUpdate.as_view(),name='profile'),
]