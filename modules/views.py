from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count
from .models import TrainingModule, UserModuleProgress, LearningPath, Notification, ModuleContent, AssessmentQuestion, UserAssessment
import datetime
import re

# Create your views here.

@login_required
def module_list(request):
    modules = TrainingModule.objects.all()
    for module in modules:
        module.user_progress = UserModuleProgress.objects.filter(
            user=request.user,
            module=module
        )
    
    # Get notifications for the user
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    unread_count = notifications.filter(is_read=False).count()
    recent_notifications = notifications[:5]
    
    context = {
        'modules': modules,
        'notifications': notifications,
        'unread_count': unread_count,
        'recent_notifications': recent_notifications,
    }
    return render(request, 'modules/module_list.html', context)

@login_required
def start_module(request, slug):
    module = get_object_or_404(TrainingModule, slug=slug)
    
    # Create or get user progress
    progress, created = UserModuleProgress.objects.get_or_create(
        user=request.user,
        module=module,
        defaults={'progress': 0, 'is_completed': False}
    )
    
    if created:
        # Notification will be created via signal
        return redirect('modules:module_detail', slug=slug)
    else:
        return redirect('modules:resume_module', slug=slug)

@login_required
def resume_module(request, slug):
    module = get_object_or_404(TrainingModule, slug=slug)
    progress = get_object_or_404(
        UserModuleProgress,
        user=request.user,
        module=module
    )
    
    # Update last accessed time
    progress.last_accessed = timezone.now()
    progress.save()
    
    return redirect('modules:module_detail', slug=slug)

@login_required
def update_progress(request, slug):
    if request.method == 'POST':
        module = get_object_or_404(TrainingModule, slug=slug)
        progress = get_object_or_404(
            UserModuleProgress,
            user=request.user,
            module=module
        )
        
        try:
            new_progress = int(request.POST.get('progress', 0))
            if 0 <= new_progress <= 100:
                progress.progress = new_progress
                if new_progress == 100:
                    progress.is_completed = True
                    progress.completed_at = timezone.now()
                progress.save()
                return JsonResponse({'success': True})
        except ValueError:
            pass
        
        return JsonResponse({'success': False, 'error': 'Invalid progress value'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def mark_notification_read(request, notification_id):
    if request.method == 'POST':
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            user=request.user
        )
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]
    
    unread_count = notifications.filter(is_read=False).count()
    recent_notifications = notifications[:5]
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
        'recent_notifications': recent_notifications,
    }
    
    return render(request, 'modules/notifications_panel.html', context)

@login_required
def start_new_course(request):
    # Get all modules
    modules = TrainingModule.objects.all().order_by('title')
    
    # Get user's progress for all modules
    user_progress = {
        progress.module_id: progress
        for progress in UserModuleProgress.objects.filter(user=request.user)
    }
    
    # Attach progress information to each module (custom attribute)
    for module in modules:
        module.current_user_progress = user_progress.get(module.id)
    
    context = {
        'modules': modules,
        'title': 'Available Courses'
    }
    return render(request, 'modules/start_new_course.html', context)

@login_required
def learning_path_list(request):
    learning_paths = LearningPath.objects.filter(is_active=True)
    
    # Calculate progress for each learning path
    for path in learning_paths:
        path.progress = path.get_progress(request.user)
        
        # Get the next available module
        available_modules = path.modules.filter(is_active=True).order_by('order')
        path.next_module = None
        for module in available_modules:
            if module.is_available_for_user(request.user):
                progress = UserModuleProgress.objects.filter(
                    user=request.user,
                    module=module
                ).first()
                if not progress or not progress.is_completed:
                    path.next_module = module
                    break
    
    context = {
        'learning_paths': learning_paths
    }
    return render(request, 'modules/learning_path_list.html', context)

@login_required
def learning_path_detail(request, path_id):
    learning_path = get_object_or_404(LearningPath, id=path_id, is_active=True)
    modules = learning_path.modules.filter(is_active=True).order_by('order')
    
    # Get user progress for all modules in this path
    user_progress = {
        progress.module_id: progress
        for progress in UserModuleProgress.objects.filter(
            user=request.user,
            module__learning_path=learning_path
        )
    }
    
    # Calculate overall progress
    total_progress = learning_path.get_progress(request.user)
    
    # Attach progress and availability information to each module
    for module in modules:
        if module.id in user_progress:
            module.user_progress = user_progress[module.id]
        else:
            module.user_progress = None
        module.is_available = module.is_available_for_user(request.user)
    
    context = {
        'learning_path': learning_path,
        'modules': modules,
        'total_progress': total_progress
    }
    return render(request, 'modules/learning_path_detail.html', context)

def get_youtube_embed_url(url):
    # Handle watch?v= and youtu.be/ and strip extra params
    if 'youtube.com/watch?v=' in url:
        video_id = url.split('watch?v=')[1].split('&')[0]
    elif 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[1].split('?')[0]
    else:
        return ''
    return f'https://www.youtube.com/embed/{video_id}'

@login_required
def module_detail(request, slug):
    module = get_object_or_404(TrainingModule, slug=slug)
    contents = module.contents.all()
    # Add embed URL for YouTube and prepare external links list
    for c in contents:
        if c.youtube_url:
            c.youtube_embed_url = get_youtube_embed_url(c.youtube_url)
        else:
            c.youtube_embed_url = ''
        if c.external_links:
            c.external_links_list = [link.strip() for link in c.external_links.split(',') if link.strip()]
        else:
            c.external_links_list = []
    user_progress, _ = UserModuleProgress.objects.get_or_create(user=request.user, module=module)
    return render(request, 'modules/module_detail.html', {
        'module': module,
        'contents': contents,
        'user_progress': user_progress,
    })

@login_required
def module_quiz(request, slug):
    module = get_object_or_404(TrainingModule, slug=slug)
    questions = module.questions.all()
    user_progress, _ = UserModuleProgress.objects.get_or_create(user=request.user, module=module)

    if request.method == 'POST':
        answers = {q.id: request.POST.get(f'q{q.id}') for q in questions}
        score = 0
        for q in questions:
            if answers[q.id] == q.correct_option:
                score += 1
        percent = int((score / questions.count()) * 100) if questions else 0
        passed = percent >= 60  # Pass threshold

        # Store assessment
        UserAssessment.objects.create(
            user=request.user,
            module=module,
            score=percent,
            passed=passed
        )
        # Update progress
        user_progress.progress = 100
        user_progress.is_completed = True
        user_progress.completed_at = timezone.now()
        user_progress.save()

        return render(request, 'modules/quiz_result.html', {
            'module': module,
            'score': percent,
            'passed': passed,
            'total': questions.count(),
            'correct': score,
        })

    return render(request, 'modules/module_quiz.html', {
        'module': module,
        'questions': questions,
        'user_progress': user_progress,
    })
