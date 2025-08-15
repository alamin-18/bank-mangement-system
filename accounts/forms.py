from django import forms
from .models import UserBankAccount, UserAddress
from django.contrib.auth.models import User
from .constants import ACCOUNT_TYPE, GENDER_TYPE
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.CharField(max_length=20)  # safer for international use
    country = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = [
            'username', 'password1', 'password2', 'first_name', 'last_name',
            'email', 'account_type', 'gender', 'street_address', 'date_of_birth',
            'city', 'postal_code', 'country'
        ]
        
    def save(self, commit=True):
        our_user = super().save(commit=False)
        if commit:
            our_user.save()
            UserAddress.objects.create(
                user=our_user,
                postal_code=self.cleaned_data.get('postal_code'),
                country=self.cleaned_data.get('country'),
                city=self.cleaned_data.get('city'),
                street_address=self.cleaned_data.get('street_address')
            )
            UserBankAccount.objects.create(
                user=our_user,
                gender=self.cleaned_data.get('gender'),
                account_type=self.cleaned_data.get('account_type'),
                date_of_birth=self.cleaned_data.get('date_of_birth'),
                account_no=2025081520 + our_user.id
            )
        return our_user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })

class UserUpdateForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.CharField(max_length=20)  # safer for international use
    country = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add CSS classes to all fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })

        if self.instance:
            try:
                user_account = self.instance.account
            except UserBankAccount.DoesNotExist:
                user_account = None

            try:
                user_address = self.instance.address
            except UserAddress.DoesNotExist:
                user_address = None

            if user_account:
                self.fields['account_type'].initial = user_account.account_type
                self.fields['gender'].initial = user_account.gender
                self.fields['date_of_birth'].initial = user_account.date_of_birth

            if user_address:
                self.fields['street_address'].initial = user_address.street_address
                self.fields['city'].initial = user_address.city
                self.fields['postal_code'].initial = user_address.postal_code
                self.fields['country'].initial = user_address.country

    def save(self, commit=True):
        user = super().save(commit=commit)

        user_account, _ = UserBankAccount.objects.get_or_create(user=user)
        user_account.account_type = self.cleaned_data['account_type']
        user_account.gender = self.cleaned_data['gender']
        user_account.date_of_birth = self.cleaned_data['date_of_birth']
        user_account.save()

        user_address, _ = UserAddress.objects.get_or_create(user=user)
        user_address.street_address = self.cleaned_data['street_address']
        user_address.city = self.cleaned_data['city']
        user_address.postal_code = self.cleaned_data['postal_code']
        user_address.country = self.cleaned_data['country']
        user_address.save()

        return user

        
    
    
            
                


