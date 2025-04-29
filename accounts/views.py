from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse, JsonResponse
import smtplib
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import UserProfile, UserActivityLog, UserBadge, UserCertificate
from .forms import ProfileUpdateForm, ProfileSettingsForm
import json
from datetime import datetime

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # Make user active immediately
            user.save()
            
            messages.success(request, f'Account created successfully! Please login to continue.')
            return redirect('accounts:login')  # Redirect to login page
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated successfully! You can now login.')
        return redirect('login')
    else:
        messages.error(request, 'The confirmation link was invalid or has expired.')
        return redirect('register')

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Add debug messages
        messages.info(request, f'Attempting login for user: {username}')
        
        if form.is_valid():
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.username}!')
                    return redirect('/dashboard/')
                else:
                    messages.error(request, 'Your account is not active.')
            else:
                messages.error(request, f'Authentication failed for user {username}. Please check your credentials.')
        else:
            # Print form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Form Error - {field}: {error}')
            
        # Instead of redirecting, render the form with errors
        return render(request, 'accounts/login.html', {'form': form})
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')

@login_required
def profile(request):
    user = request.user
    profile = user.user_profile
    activity_logs = UserActivityLog.objects.filter(user=user).order_by('-timestamp')[:5]
    badges = UserBadge.objects.filter(user=user)
    certificates = UserCertificate.objects.filter(user=user)
    
    # Get progress statistics
    completed_modules = user.module_progress.filter(is_completed=True).count()
    total_modules = user.module_progress.count()
    completion_percentage = (completed_modules / total_modules * 100) if total_modules > 0 else 0
    
    context = {
        'user': user,
        'profile': profile,
        'activity_logs': activity_logs,
        'badges': badges,
        'certificates': certificates,
        'completed_modules': completed_modules,
        'completion_percentage': completion_percentage,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def profile_settings(request):
    if request.method == 'POST':
        form = ProfileSettingsForm(request.POST, request.FILES, instance=request.user.user_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            
            # Handle profile photo upload
            if 'profile_photo' in request.FILES:
                photo = request.FILES['profile_photo']
                file_name = f"profile_photos/{request.user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{photo.name}"
                file_path = default_storage.save(file_name, ContentFile(photo.read()))
                profile.profile_photo = file_path
            
            profile.save()
            profile.calculate_profile_complete()
            messages.success(request, 'Profile settings updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileSettingsForm(instance=request.user.user_profile)
    
    context = {
        'form': form,
        'profile': request.user.user_profile
    }
    return render(request, 'accounts/profile_settings.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile_settings')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form
    }
    return render(request, 'accounts/change_password.html', context)

@login_required
def toggle_mfa(request):
    if request.method == 'POST':
        profile = request.user.user_profile
        profile.mfa_enabled = not profile.mfa_enabled
        profile.save()
        
        # Log the activity
        UserActivityLog.objects.create(
            user=request.user,
            activity_type='MFA_TOGGLE',
            ip_address=request.META.get('REMOTE_ADDR'),
            device_info=request.META.get('HTTP_USER_AGENT', ''),
            details=f"MFA {'enabled' if profile.mfa_enabled else 'disabled'}"
        )
        
        return JsonResponse({
            'success': True,
            'mfa_enabled': profile.mfa_enabled
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def update_notification_preferences(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            profile = request.user.user_profile
            profile.email_notifications = data.get('email_notifications', profile.email_notifications)
            profile.weekly_summary = data.get('weekly_summary', profile.weekly_summary)
            profile.save()
            
            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def download_user_data(request):
    user = request.user
    profile = user.user_profile
    
    data = {
        'user_info': {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
        },
        'profile_info': {
            'department': profile.department,
            'team': profile.team,
            'mfa_enabled': profile.mfa_enabled,
            'email_notifications': profile.email_notifications,
            'weekly_summary': profile.weekly_summary,
            'profile_complete': profile.profile_complete,
        },
        'activity_logs': [
            {
                'activity_type': log.activity_type,
                'timestamp': log.timestamp.isoformat(),
                'ip_address': log.ip_address,
                'device_info': log.device_info,
                'details': log.details
            }
            for log in UserActivityLog.objects.filter(user=user)
        ],
        'badges': [
            {
                'name': badge.name,
                'description': badge.description,
                'earned_at': badge.earned_at.isoformat()
            }
            for badge in UserBadge.objects.filter(user=user)
        ],
        'certificates': [
            {
                'title': cert.title,
                'description': cert.description,
                'issued_at': cert.issued_at.isoformat(),
                'expires_at': cert.expires_at.isoformat() if cert.expires_at else None
            }
            for cert in UserCertificate.objects.filter(user=user)
        ]
    }
    
    response = JsonResponse(data)
    response['Content-Disposition'] = f'attachment; filename="{user.username}_data.json"'
    return response

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.is_active = False
        user.save()
        
        # Log the activity
        UserActivityLog.objects.create(
            user=user,
            activity_type='ACCOUNT_DEACTIVATED',
            ip_address=request.META.get('REMOTE_ADDR'),
            device_info=request.META.get('HTTP_USER_AGENT', ''),
            details='Account deactivated by user'
        )
        
        messages.success(request, 'Your account has been deactivated.')
        return redirect('accounts:login')
    
    return render(request, 'accounts/delete_account.html')
