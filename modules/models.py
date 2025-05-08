from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Max
from django.utils.text import slugify
from django.contrib.postgres.fields import JSONField
from django_ckeditor_5.fields import CKEditor5Field

User = get_user_model()

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
    overview = CKEditor5Field('Overview', blank=True, help_text="Overview or structure of the learning path (supports rich text)")
    
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
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Bootstrap icon class or image URL")
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
    is_active = models.BooleanField(default=True, help_text="Designates whether this module is active.")
    order = models.PositiveIntegerField(default=1, help_text="Order of this module in the learning path")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def content(self):
        """Get the combined content of all module sections"""
        return "\n\n".join(section.content for section in self.contents.all().order_by('order'))

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
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE, related_name='user_progress')
    progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Progress percentage (0-100)"
    )
    is_completed = models.BooleanField(default=False)
    last_accessed = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'module']
        ordering = ['-last_accessed']
        verbose_name = "User Module Progress"
        verbose_name_plural = "User Module Progress Records"

    def __str__(self):
        return f"{self.user.username} - {self.module.title} ({self.progress}%)"

    def save(self, *args, **kwargs):
        if self.progress == 100 and not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_notifications')
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}"

class ModuleContent(models.Model):
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE, related_name='contents')
    text = CKEditor5Field('Content', help_text='Learning material (rich text, HTML allowed)')
    youtube_url = models.URLField(blank=True, null=True, help_text='YouTube video URL (optional)')
    external_links = models.TextField(blank=True, help_text='Comma-separated URLs for external resources (optional)')
    order = models.PositiveIntegerField(default=1, help_text='Order of content sections')

    class Meta:
        ordering = ['order']
        verbose_name = 'Module Content'
        verbose_name_plural = 'Module Contents'

    def __str__(self):
        return f"{self.module.title} - Section {self.order}"

class AssessmentQuestion(models.Model):
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')])

    def __str__(self):
        return f"{self.module.title} - {self.question[:40]}..."

class UserAssessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessments')
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE, related_name='user_assessments')
    score = models.PositiveIntegerField()
    passed = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.module.title} - {self.score} pts"
