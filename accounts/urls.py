from django.urls import path
from .views import UserRegistationsForms,UserBankAccountUpdate,UserLoginView,UserLogoutView

urlpatterns = [
   
    path('register/', UserRegistationsForms.as_view(),name='register'),
    path('profile/', UserBankAccountUpdate.as_view(),name='profile'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
]