from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import TrainingModule, UserModuleProgress
import datetime

# Create your views here.

@login_required
def module_list(request):
    # Get all active modules
    modules = TrainingModule.objects.filter(is_active=True)
    
    # Get user's progress for all modules
    user_progress = {
        progress.module_id: progress
        for progress in UserModuleProgress.objects.filter(user=request.user)
    }
    
    # Attach progress information to each module
    for module in modules:
        if module.id in user_progress:
            module.user_progress = user_progress[module.id]
        else:
            module.user_progress = None

    context = {
        'modules': modules
    }
    return render(request, 'modules/module_list.html', context)

@login_required
def start_module(request, module_id):
    module = get_object_or_404(TrainingModule, id=module_id, is_active=True)
    
    # Check if user already has progress for this module
    progress = UserModuleProgress.objects.filter(
        user=request.user,
        module=module
    ).first()
    
    if progress:
        # If progress exists, redirect to module detail
        return redirect('modules:module_detail', module_id=module_id)
    else:
        # Create new progress record
        progress = UserModuleProgress.objects.create(
            user=request.user,
            module=module,
            completion_percentage=0,
            is_completed=False,
            started_at=timezone.now(),
            last_accessed=timezone.now()
        )
        return redirect('modules:module_detail', module_id=module_id)

@login_required
def module_detail(request, module_id):
    module = get_object_or_404(TrainingModule, id=module_id, is_active=True)
    
    # Get or create progress record
    progress, created = UserModuleProgress.objects.get_or_create(
        user=request.user,
        module=module,
        defaults={
            'completion_percentage': 0,
            'is_completed': False,
            'started_at': timezone.now(),
            'last_accessed': timezone.now()
        }
    )
    
    # Update last accessed time and calculate time spent
    if not created:
        current_time = timezone.now()
        time_diff = current_time - progress.last_accessed
        
        # Only update time spent if the difference is significant (e.g., more than 1 minute)
        if time_diff.total_seconds() > 60:
            progress.time_spent = (progress.time_spent or datetime.timedelta()) + time_diff
            progress.last_accessed = current_time
            progress.save()
    
    context = {
        'module': module,
        'progress': progress
    }
    return render(request, 'modules/module_detail.html', context)

@login_required
def update_progress(request, module_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    module = get_object_or_404(TrainingModule, id=module_id, is_active=True)
    progress = get_object_or_404(UserModuleProgress, user=request.user, module=module)
    
    try:
        new_percentage = int(request.POST.get('percentage', 0))
        if 0 <= new_percentage <= 100:
            progress.completion_percentage = new_percentage
            
            # Update completion status
            if new_percentage == 100 and not progress.is_completed:
                progress.is_completed = True
                progress.completed_at = timezone.now()
            
            # Update time spent
            current_time = timezone.now()
            time_diff = current_time - progress.last_accessed
            if time_diff.total_seconds() > 60:  # Only update if more than 1 minute
                progress.time_spent = (progress.time_spent or datetime.timedelta()) + time_diff
                progress.last_accessed = current_time
            
            progress.save()
            return JsonResponse({
                'success': True,
                'percentage': progress.completion_percentage,
                'is_completed': progress.is_completed,
                'time_spent': str(progress.time_spent)
            })
    except ValueError:
        pass
        
    return JsonResponse({'error': 'Invalid percentage value'}, status=400)

@login_required
def start_new_course(request):
    # Get all active modules
    modules = TrainingModule.objects.filter(is_active=True).order_by('order', 'title')
    
    # Get user's progress for all modules
    user_progress = {
        progress.module_id: progress
        for progress in UserModuleProgress.objects.filter(user=request.user)
    }
    
    # Attach progress information to each module
    for module in modules:
        if module.id in user_progress:
            module.user_progress = user_progress[module.id]
        else:
            module.user_progress = None
    
    context = {
        'modules': modules,
        'title': 'Available Courses'
    }
    return render(request, 'modules/start_new_course.html', context)
