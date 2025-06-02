from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, FreelancerProfile, ClientProfile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    phone_number = forms.CharField(max_length=20)
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 
                  'phone_number', 'user_type', 
                  'password1', 'password2']

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number']

class FreelancerProfileForm(forms.ModelForm):
    class Meta:
        model = FreelancerProfile
        fields = ['skills', 'hourly_rate', 'bio', 'portfolio_url']

class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = ['company', 'industry']
