from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
import re
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', password1):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password1):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'[0-9]', password1):
            raise forms.ValidationError("Password must contain at least one number.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
            raise forms.ValidationError("Password must contain at least one special character.")
        return password1

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    remember_me = forms.BooleanField(required=False, initial=False)

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['department', 'team', 'profile_photo', 'email_notifications', 
                 'weekly_summary', 'show_in_leaderboard', 'dark_mode']
        widgets = {
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'team': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'weekly_summary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_in_leaderboard': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dark_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'}) 