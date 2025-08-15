from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views.generic import FormView,View
from .forms import RegistrationForm,UserUpdateFrom
from django.contrib.auth import login,logout
from django.contrib.auth.views import LoginView, LogoutView


class UserRegistationsForms(FormView):
    template_name = 'accounts/registations_form.html'
    form_class = RegistrationForm  
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)
    
class UserBankAccountUpdate(View):
    tampalte_name = 'accounts/profile.html'
    def get(self,request):
        form = UserUpdateFrom(instance=request.user)
        return render(request,self.tampalte_name,{'form':form})
    def post(self,request):
        form = UserUpdateFrom(request.POST,instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request,self.template_name,{'form':form})


class UserLogOut(LogoutView):
    def get_success_url(self):
        if self.request.user.is_authenticated:
            login(self.request)
        return reverse_lazy('home')
