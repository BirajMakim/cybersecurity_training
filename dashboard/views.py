from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from modules.models import UserModuleProgress, TrainingModule
from django.db.models import Sum, Count, F, ExpressionWrapper, DurationField
from django.utils import timezone
import datetime
from accounts.models import UserProfile, UserActivityLog, UserBadge, UserCertificate
from django.http import JsonResponse
from django.db.models import Q
from .models import Notification
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
import json

class DashboardContextMixin:
    """Mixin to add common context data to dashboard views"""
    def get_common_context(self, request):
        return {
            'unread_notifications_count': Notification.objects.filter(
                user=request.user, 
                is_read=False
            ).count()
        }

@login_required
def profile_redirect(request):
    return redirect('accounts:profile')

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
        'unread_notifications_count': Notification.objects.filter(user=user, is_read=False).count()
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
    # Get all notifications for the user
    notifications_list = Notification.objects.filter(user=request.user)
    
    # Paginate notifications
    paginator = Paginator(notifications_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'unread_count': notifications_list.filter(is_read=False).count(),
        'unread_notifications_count': notifications_list.filter(is_read=False).count()
    }
    return render(request, 'dashboard/notifications.html', context)

@login_required
@require_POST
def mark_notification_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)

@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})

@login_required
def get_unread_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})

@login_required
def get_latest_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')[:5]
    data = [{
        'id': n.id,
        'message': n.message,
        'type': n.type,
        'is_read': n.is_read,
        'timestamp': n.timestamp.isoformat(),
        'link': n.link,
        'icon': n.get_icon_class(),
        'alert_class': n.get_alert_class(),
    } for n in notifications]
    return JsonResponse({'notifications': data})

@login_required
def settings(request):
    return render(request, 'dashboard/settings.html') 