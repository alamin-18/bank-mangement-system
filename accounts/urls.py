from django.urls import path
from .views import UserRegistationsForms,UserBankAccountUpdate,UserLoginView,user_logout

urlpatterns = [
   
    path('register/', UserRegistationsForms.as_view(),name='register'),
    path('profile/', UserBankAccountUpdate.as_view(),name='profile'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', user_logout, name='logout'),
]