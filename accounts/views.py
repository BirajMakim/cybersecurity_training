from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.shortcuts import render, redirect
from django.core.mail import send_mail, EmailMessage
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse, JsonResponse
from django.contrib.sites.shortcuts import get_current_site
import smtplib
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm, CustomPasswordChangeForm, UserProfileForm
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import UserProfile, UserActivityLog, UserBadge, UserCertificate
from .forms import ProfileUpdateForm, ProfileSettingsForm, ProfileEditForm
from .tokens import account_activation_token
import json
from datetime import datetime
from dashboard.utils import create_user_notification
from django.urls import reverse

def send_activation_email(request, user, to_email):
    mail_subject = "Activate your account"
    message = render_to_string("accounts/email_activation.html", {
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear {user.username}, please go to your email {to_email} inbox and click on the received activation link to confirm and complete the registration. Note: Check your spam folder.')
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Create the user
            user = form.save(commit=False)
            user.is_active = False  # User is not active until email verification
            user.save()
            
            # Update or create the UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.first_name = form.cleaned_data['first_name']
            profile.last_name = form.cleaned_data['last_name']
            profile.email = form.cleaned_data['email']
            profile.save()
            
            # Send activation email
            send_activation_email(request, user, form.cleaned_data['email'])
            
            # Create a success message
            messages.success(
                request, 
                'Please check your email to complete the registration process.'
            )
            
            # Redirect to login page
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        print(f"Found user: {user.username}, is_active: {user.is_active}")
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        print("User not found or invalid uid")

    if user is not None and account_activation_token.check_token(user, token):
        print(f"Token is valid for user: {user.username}")
        user.is_active = True
        user.save()
        print(f"User activated: {user.username}, is_active: {user.is_active}")
        
        # Update the profile verification status
        try:
            profile = user.user_profile
            profile.email = user.email
            profile.save()
            print(f"Profile updated for user: {user.username}")
        except Exception as e:
            print(f"Error updating profile: {str(e)}")
        
        messages.success(request, 'Your account has been activated successfully! You can now login.')
        return redirect('accounts:login')
    else:
        print(f"Token validation failed for user: {user.username if user else 'None'}")
        messages.error(request, 'The confirmation link was invalid or has expired.')
        return redirect('accounts:register')

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        print(f"Login attempt for username: {username}")
        
        if form.is_valid():
            print("Form is valid")
            user = authenticate(username=username, password=password)
            print(f"Authentication result: {user is not None}")
            
            if user is not None:
                print(f"User found: {user.username}, is_active: {user.is_active}")
                if not user.is_active:
                    print(f"User {user.username} is not active")
                    messages.error(request, 'Please verify your email address before logging in.')
                    return redirect('accounts:login')
                
                login(request, user)
                print(f"User {user.username} logged in successfully")
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('/dashboard/')
            else:
                print(f"Authentication failed for user: {username}")
                messages.error(request, 'Invalid username or password. Please try again.')
                return redirect('accounts:login')
        else:
            print(f"Form validation failed: {form.errors}")
            messages.error(request, 'Invalid username or password. Please try again.')
            return redirect('accounts:login')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')

@login_required
def profile_view(request):
    user = request.user
    profile = user.user_profile
    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'accounts/profile_view.html', context)

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
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in
            
            # Log the activity
            UserActivityLog.objects.create(
                user=request.user,
                activity_type='PASSWORD_CHANGE',
                ip_address=request.META.get('REMOTE_ADDR'),
                device_info=request.META.get('HTTP_USER_AGENT', ''),
                details='Password changed successfully'
            )
            
            # Send email notification
            try:
                send_mail(
                    'Password Changed Successfully',
                    f'Hello {user.get_full_name()},\n\nYour password has been changed successfully. If you did not make this change, please contact support immediately.\n\nBest regards,\nThe {settings.SITE_NAME} Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log the email error but don't fail the password change
                print(f"Failed to send password change email: {e}")
            
            messages.success(request, 'Your password has been updated successfully!')
            return redirect('accounts:password_change_done')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/password_change.html', context)

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

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.user_profile)
        if form.is_valid():
            old_profile = request.user.user_profile
            profile = form.save(commit=False)
            
            # Check what fields changed and create notifications
            if old_profile.email != profile.email:
                create_user_notification(
                    request.user,
                    f"Your email has been updated to {profile.email}",
                    'success'
                )
            
            if request.FILES.get('profile_photo'):
                create_user_notification(
                    request.user,
                    "Your profile photo has been updated",
                    'success'
                )
            
            if (old_profile.first_name != profile.first_name or 
                old_profile.last_name != profile.last_name):
                create_user_notification(
                    request.user,
                    "Your name has been updated",
                    'success'
                )
            
            if old_profile.department != profile.department:
                create_user_notification(
                    request.user,
                    f"Your department has been updated to {profile.department}",
                    'info'
                )
            
            profile.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user.user_profile)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})

@login_required
def password_change(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            
            # Create notification for password change
            create_user_notification(
                request.user,
                "Your password has been changed successfully",
                'success'
            )
            
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'accounts/password_change.html', {'form': form})

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                # Generate password reset token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Create reset link
                reset_link = request.build_absolute_uri(
                    reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )
                
                # Send email
                subject = "Password Reset Request"
                message = f"""
                Hello {user.username},
                
                You're receiving this email because you requested a password reset for your account.
                
                Please go to the following page and choose a new password:
                {reset_link}
                
                If you didn't request this, please ignore this email.
                
                Best regards,
                The {settings.SITE_NAME} Team
                """
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                messages.success(request, 'Password reset email has been sent. Please check your inbox.')
                return redirect('accounts:login')
            else:
                messages.error(request, 'Your account is not active. Please verify your email first.')
                return redirect('accounts:login')
        except User.DoesNotExist:
            messages.error(request, 'No user found with that email address.')
            return redirect('accounts:password_reset')
    
    return render(request, 'accounts/password_reset.html')

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            password = request.POST.get("password")
            password2 = request.POST.get("password2")
            
            if password != password2:
                messages.error(request, "Passwords don't match.")
                return render(request, 'accounts/password_reset_confirm.html')
            
            # Set new password
            user.set_password(password)
            user.save()
            
            messages.success(request, 'Your password has been reset successfully. You can now login.')
            return redirect('accounts:login')
        
        return render(request, 'accounts/password_reset_confirm.html')
    else:
        messages.error(request, 'The password reset link is invalid or has expired.')
        return redirect('accounts:password_reset')
