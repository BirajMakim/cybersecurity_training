from django.core.management.base import BaseCommand
from modules.models import TrainingModule

class Command(BaseCommand):
    help = 'Adds the Phishing Awareness module to the training modules'

    def handle(self, *args, **options):
        module, created = TrainingModule.objects.get_or_create(
            title='Phishing Awareness',
            defaults={
                'description': 'Learn how to identify and prevent phishing attacks',
                'estimated_duration': 45,
                'difficulty': 'basic',
                'icon_name': 'envelope-exclamation',
                'order': 1,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created Phishing Awareness module'))
        else:
            self.stdout.write(self.style.WARNING('Phishing Awareness module already exists')) 