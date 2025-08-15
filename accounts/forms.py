from django import forms
from .models import UserBankAccount,UserAddress
from django.contrib.auth.models import User
from .constants import ACCOUNT_TYPE,GENDER_TYPE
from django.contrib.auth.forms import UserCreationForm

class RegistationForms(UserCreationForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    steet_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    country = forms.CharField(default='Bangladesh',max_length=100)
    
    class Meta:
        model=User
        fields=['username','password1','password2','first_name','last_name','eamil','account_type','gender','steet_address','date_of_birth','city','posta;_code','country']
        
    def save(self, commit = True):
        our_user= super().save(commit =False)
        if commit == True:
            our_user.save()
            account_type= self.cleaned_data.get('account_type')
            gender= self.cleaned_data.get('gender')
            date_of_birth= self.cleaned_data.get('date_of_birth')
            country= self.cleaned_data.get('country')
            postal_code= self.cleaned_data.get('postal_code')
            city= self.cleaned_data.get('city')
            street_address= self.cleaned_data.get('street_address')
            
            UserAddress.objects.create(
                user = our_user,
                postal_code=postal_code,
                country = country,
                city = city,
                street_address = street_address
                
            )
            UserBankAccount.objects.create(
                user =our_user,
                gender =gender,
                account_type=account_type,
                date_of_birth =date_of_birth,
                account_no = 2025081520 + our_user.id
            )
            return our_user