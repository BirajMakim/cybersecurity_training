from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from modules.models import UserModuleProgress, TrainingModule
from django.db.models import Sum, Count, F, ExpressionWrapper, DurationField
from django.utils import timezone
import datetime
from accounts.models import UserProfile, UserActivityLog, UserBadge, UserCertificate

@login_required
def dashboard(request):
    user = request.user
    profile = user.user_profile
    
    # Get progress statistics
    completed_modules = user.module_progress.filter(is_completed=True).count()
    total_modules = user.module_progress.count()
    total_progress = (completed_modules / total_modules * 100) if total_modules > 0 else 0
    
    # Calculate total time spent
    total_time_spent = user.module_progress.aggregate(
        total_time=Sum('time_spent')
    )['total_time'] or datetime.timedelta()
    
    # Convert timedelta to hours
    total_hours = round(total_time_spent.total_seconds() / 3600, 1)
    
    # Get current courses (in-progress modules)
    current_courses = user.module_progress.filter(
        is_completed=False,
        completion_percentage__gt=0
    ).select_related('module').order_by('-last_accessed')
    
    # Get recent activity
    recent_activity = user.module_progress.order_by('-last_accessed')[:5]
    
    context = {
        'user': user,
        'profile': profile,
        'completed_modules': completed_modules,
        'total_progress': round(total_progress, 1),
        'total_hours': total_hours,
        'current_courses': current_courses,
        'recent_activity': recent_activity,
    }
    return render(request, 'dashboard/index.html', context)

@login_required
def learning_path(request):
    return render(request, 'dashboard/learning_path.html')

@login_required
def phishing(request):
    return render(request, 'dashboard/phishing.html')

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
def notifications(request):
    return render(request, 'dashboard/notifications.html')

@login_required
def settings(request):
    return render(request, 'dashboard/settings.html') 