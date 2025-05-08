from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from modules.models import UserModuleProgress, TrainingModule, LearningPath
from django.db.models import Sum, Count, F, ExpressionWrapper, DurationField
from django.utils import timezone
import datetime
from accounts.models import UserProfile, UserActivityLog, UserBadge, UserCertificate
from django.http import JsonResponse
from django.db.models import Q
from .models import Notification
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
import json
import logging

logger = logging.getLogger(__name__)

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
    try:
        user = request.user
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            }
        )
        
        # Get progress statistics
        total_modules = TrainingModule.objects.all().count()
        if total_modules > 0:
            completed_modules = UserModuleProgress.objects.filter(
                user=user,
                is_completed=True
            ).count()
            total_progress = (completed_modules / total_modules * 100)
        else:
            completed_modules = 0
            total_progress = 0
        
        # Get current courses (in-progress modules)
        current_courses = UserModuleProgress.objects.filter(
            user=user,
            is_completed=False
        ).select_related('module').order_by('-last_accessed')
        
        # Get recent activity
        recent_activity = UserModuleProgress.objects.filter(
            user=user
        ).select_related('module').order_by('-last_accessed')[:5]
        
        # Calculate hours spent
        progress_records = UserModuleProgress.objects.filter(user=user)
        total_seconds = 0
        for record in progress_records:
            if record.is_completed and record.completed_at and record.started_at:
                total_seconds += (record.completed_at - record.started_at).total_seconds()
            elif record.started_at:
                end_time = record.last_accessed or timezone.now()
                total_seconds += (end_time - record.started_at).total_seconds()
        hours_spent = round(total_seconds / 3600, 2)
        
        context = {
            'user': user,
            'profile': profile,
            'completed_modules': completed_modules,
            'total_progress': round(total_progress, 1),
            'current_courses': current_courses,
            'recent_activity': recent_activity,
            'unread_notifications_count': Notification.objects.filter(
                user=user,
                is_read=False
            ).count(),
            'hours_spent': hours_spent,
        }
        return render(request, 'dashboard/index.html', context)
        
    except Exception as e:
        logger.error(f"Error in dashboard view: {str(e)}")
        context = {
            'error_message': "An error occurred while loading the dashboard. Please try again later."
        }
        return render(request, 'dashboard/error.html', context)

@login_required
def learning_path(request):
    return redirect('modules:learning_path_list')

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
@ensure_csrf_cookie
def notifications(request):
    try:
        # Get all notifications for the user
        notifications_list = Notification.objects.filter(user=request.user)
        print('DEBUG: notifications_list:', list(notifications_list))  # Debug print
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
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_POST
def mark_notification_read(request, notification_id):
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def mark_all_read(request):
    try:
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_unread_count(request):
    try:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return JsonResponse({'count': count})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_latest_notifications(request):
    try:
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
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def settings(request):
    return render(request, 'dashboard/settings.html')

@login_required
def search_view(request):
    query = request.GET.get('q', '')
    context = {'query': query}
    
    if query:
        # Search in Training Modules
        modules = TrainingModule.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(difficulty__icontains=query)
        )
        
        # Search in Learning Paths
        paths = LearningPath.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
        
        # Search in Activity Logs
        activities = UserActivityLog.objects.filter(
            Q(activity_type__icontains=query) |
            Q(details__icontains=query)
        ).select_related('user')[:10]  # Limit to 10 most recent
        
        context.update({
            'modules': modules,
            'paths': paths,
            'activities': activities,
            'has_results': any([modules.exists(), paths.exists(), activities.exists()])
        })
    
    return render(request, 'dashboard/search_results.html', context) 