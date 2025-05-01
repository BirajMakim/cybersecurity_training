from django.core.management.base import BaseCommand
from modules.models import LearningPath, TrainingModule

class Command(BaseCommand):
    help = 'Creates initial learning paths and organizes existing modules'

    def handle(self, *args, **options):
        # Create learning paths
        paths = [
            {
                'name': 'Cybersecurity Fundamentals',
                'description': 'Master the essential concepts and practices of cybersecurity',
                'order': 1,
                'icon_name': 'shield-lock',
                'modules': [
                    'Introduction to Cybersecurity',
                    'Password Security & Authentication',
                    'Phishing Awareness',
                    'Secure Web Browsing'
                ]
            },
            {
                'name': 'Advanced Security',
                'description': 'Dive deep into advanced cybersecurity concepts and techniques',
                'order': 2,
                'icon_name': 'shield-check',
                'modules': [
                    'Network Security Fundamentals',
                    'Data Protection & Privacy',
                    'Social Engineering Defense',
                    'Incident Response'
                ]
            },
            {
                'name': 'Specialized Training',
                'description': 'Focus on specific areas of cybersecurity expertise',
                'order': 3,
                'icon_name': 'gear',
                'modules': [
                    'Mobile Security',
                    'Secure Software Development'
                ]
            }
        ]

        for path_data in paths:
            path, created = LearningPath.objects.get_or_create(
                name=path_data['name'],
                defaults={
                    'description': path_data['description'],
                    'order': path_data['order'],
                    'icon_name': path_data['icon_name'],
                    'is_active': True
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created learning path: {path.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Learning path already exists: {path.name}'))

            # Assign modules to path
            for i, module_title in enumerate(path_data['modules']):
                try:
                    module = TrainingModule.objects.get(title=module_title)
                    module.learning_path = path
                    module.order = i + 1
                    module.save()
                    self.stdout.write(f'Assigned module "{module_title}" to path "{path.name}"')
                except TrainingModule.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'Module not found: {module_title}')
                    )

        # Set up prerequisites
        self.setup_prerequisites()

    def setup_prerequisites(self):
        """Set up prerequisites for modules that require them"""
        # Get modules by title
        try:
            intro = TrainingModule.objects.get(title='Introduction to Cybersecurity')
            password = TrainingModule.objects.get(title='Password Security & Authentication')
            phishing = TrainingModule.objects.get(title='Phishing Awareness')
            network = TrainingModule.objects.get(title='Network Security Fundamentals')
            data_protection = TrainingModule.objects.get(title='Data Protection & Privacy')
            social = TrainingModule.objects.get(title='Social Engineering Defense')
            incident = TrainingModule.objects.get(title='Incident Response')
            secure_dev = TrainingModule.objects.get(title='Secure Software Development')

            # Set prerequisites
            password.prerequisites.add(intro)
            phishing.prerequisites.add(intro)
            network.prerequisites.add(password)
            data_protection.prerequisites.add(network)
            social.prerequisites.add(phishing)
            incident.prerequisites.add(data_protection, social)
            secure_dev.prerequisites.add(network)

            self.stdout.write(self.style.SUCCESS('Successfully set up module prerequisites'))
        except TrainingModule.DoesNotExist:
            self.stdout.write(self.style.WARNING('One or more modules not found')) 