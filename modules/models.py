from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Max

# Create your models here.

class LearningPath(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(default=0, help_text="Order in which the learning path appears")
    icon_name = models.CharField(max_length=50, help_text="Bootstrap icon name", default='mortarboard')
    auto_unlock = models.BooleanField(default=False, help_text="If True, modules will unlock automatically regardless of prerequisites")
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Learning Path"
        verbose_name_plural = "Learning Paths"

    def __str__(self):
        return self.name

    def get_modules(self):
        """Get all active modules in this path, ordered by their position"""
        return self.modules.filter(is_active=True).order_by('order')

    def get_progress(self, user):
        """Calculate user's progress in this learning path"""
        total_modules = self.modules.filter(is_active=True).count()
        if total_modules == 0:
            return 0
        completed_modules = UserModuleProgress.objects.filter(
            user=user,
            module__learning_path=self,
            module__is_active=True,
            is_completed=True
        ).count()
        return (completed_modules / total_modules) * 100

    def get_next_available_module(self, user):
        """Get the next module that the user can take"""
        for module in self.get_modules():
            if module.is_available_for_user(user):
                progress = UserModuleProgress.objects.filter(
                    user=user,
                    module=module
                ).first()
                if not progress or not progress.is_completed:
                    return module
        return None

    def reorder_modules(self):
        """Reorder all modules in this path to ensure consistent ordering"""
        modules = self.get_modules()
        for index, module in enumerate(modules, 1):
            if module.order != index:
                module.order = index
                module.save(update_fields=['order'])

class TrainingModule(models.Model):
    DIFFICULTY_CHOICES = [
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    content = models.TextField(help_text="Module content in HTML format", null=True, blank=True)
    estimated_duration = models.IntegerField(help_text="Duration in minutes")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='basic')
    icon_name = models.CharField(max_length=50, help_text="Bootstrap icon name (e.g., 'shield-lock')", default='book')
    order = models.IntegerField(default=0, help_text="Order in which the module appears in its learning path")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    learning_path = models.ForeignKey(
        LearningPath,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='modules'
    )
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='dependent_modules'
    )
    completion_badge = models.CharField(
        max_length=50,
        blank=True,
        help_text="Bootstrap icon name for completion badge"
    )

    class Meta:
        ordering = ['learning_path', 'order', 'title']
        verbose_name = "Training Module"
        verbose_name_plural = "Training Modules"

    def __str__(self):
        return self.title

    def is_available_for_user(self, user):
        """Check if this module is available for the user"""
        # If the learning path allows auto-unlock, module is always available
        if self.learning_path and self.learning_path.auto_unlock:
            return True
            
        if not self.prerequisites.exists():
            return True
            
        return all(
            UserModuleProgress.objects.filter(
                user=user,
                module=prereq,
                is_completed=True
            ).exists()
            for prereq in self.prerequisites.all()
        )

    def get_next_order(self):
        """Get the next available order number in the module's learning path"""
        if not self.learning_path:
            return 1
        last_order = self.learning_path.modules.aggregate(Max('order'))['order__max']
        return (last_order or 0) + 1

    def save(self, *args, **kwargs):
        # If this is a new module or learning path has changed, set order
        if not self.pk or 'learning_path' in kwargs.get('update_fields', []):
            self.order = self.get_next_order()
        super().save(*args, **kwargs)

@receiver(pre_save, sender=TrainingModule)
def handle_module_path_change(sender, instance, **kwargs):
    """Handle module learning path changes"""
    if instance.pk:  # If this is an existing module
        old_instance = TrainingModule.objects.get(pk=instance.pk)
        if old_instance.learning_path != instance.learning_path:
            # Module is being moved to a new path or removed from one
            if old_instance.learning_path:
                # Reorder modules in the old path
                old_instance.learning_path.reorder_modules()
            if instance.learning_path:
                # Set order to be last in new path
                instance.order = instance.get_next_order()

@receiver(post_save, sender=TrainingModule)
def update_module_order(sender, instance, created, **kwargs):
    """Maintain module order after save"""
    if instance.learning_path:
        instance.learning_path.reorder_modules()

class UserModuleProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE)
    completion_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.DurationField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'module']
        ordering = ['-last_accessed']
        verbose_name = "User Module Progress"
        verbose_name_plural = "User Module Progress Records"

    def __str__(self):
        return f"{self.user.username} - {self.module.title} ({self.completion_percentage}%)"

    def save(self, *args, **kwargs):
        if self.completion_percentage == 100 and not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)
