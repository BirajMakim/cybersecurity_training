from django.core.management.base import BaseCommand
from modules.models import TrainingModule

class Command(BaseCommand):
    help = 'Adds comprehensive cybersecurity training modules'

    def handle(self, *args, **options):
        modules = [
            {
                'title': 'Introduction to Cybersecurity',
                'description': 'Learn the fundamentals of cybersecurity, including basic concepts, terminology, and the importance of security in the digital world.',
                'estimated_duration': 60,
                'difficulty': 'basic',
                'icon_name': 'shield-lock',
                'order': 1,
                'is_active': True
            },
            {
                'title': 'Password Security & Authentication',
                'description': 'Master the art of creating strong passwords, understanding multi-factor authentication, and implementing secure login practices.',
                'estimated_duration': 45,
                'difficulty': 'basic',
                'icon_name': 'key',
                'order': 2,
                'is_active': True
            },
            {
                'title': 'Phishing Awareness',
                'description': 'Learn how to identify and prevent phishing attacks, recognize suspicious emails, and protect yourself from social engineering.',
                'estimated_duration': 45,
                'difficulty': 'basic',
                'icon_name': 'envelope-exclamation',
                'order': 3,
                'is_active': True
            },
            {
                'title': 'Network Security Fundamentals',
                'description': 'Understand network security concepts, including firewalls, VPNs, and secure network configurations.',
                'estimated_duration': 90,
                'difficulty': 'intermediate',
                'icon_name': 'diagram-3',
                'order': 4,
                'is_active': True
            },
            {
                'title': 'Secure Web Browsing',
                'description': 'Learn best practices for secure web browsing, including HTTPS, browser security settings, and safe online behavior.',
                'estimated_duration': 45,
                'difficulty': 'basic',
                'icon_name': 'globe',
                'order': 5,
                'is_active': True
            },
            {
                'title': 'Data Protection & Privacy',
                'description': 'Understand data protection principles, privacy laws, and how to handle sensitive information securely.',
                'estimated_duration': 60,
                'difficulty': 'intermediate',
                'icon_name': 'database-lock',
                'order': 6,
                'is_active': True
            },
            {
                'title': 'Mobile Security',
                'description': 'Learn about mobile device security, app permissions, and how to protect your mobile data.',
                'estimated_duration': 45,
                'difficulty': 'basic',
                'icon_name': 'phone',
                'order': 7,
                'is_active': True
            },
            {
                'title': 'Social Engineering Defense',
                'description': 'Understand social engineering tactics and how to protect yourself from manipulation attempts.',
                'estimated_duration': 60,
                'difficulty': 'intermediate',
                'icon_name': 'people',
                'order': 8,
                'is_active': True
            },
            {
                'title': 'Incident Response',
                'description': 'Learn how to respond to security incidents, report breaches, and implement recovery procedures.',
                'estimated_duration': 90,
                'difficulty': 'advanced',
                'icon_name': 'exclamation-triangle',
                'order': 9,
                'is_active': True
            },
            {
                'title': 'Secure Software Development',
                'description': 'Understand secure coding practices, common vulnerabilities, and how to develop secure applications.',
                'estimated_duration': 120,
                'difficulty': 'advanced',
                'icon_name': 'code-slash',
                'order': 10,
                'is_active': True
            }
        ]

        for module_data in modules:
            module, created = TrainingModule.objects.get_or_create(
                title=module_data['title'],
                defaults=module_data
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created module: {module.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Module already exists: {module.title}'))

        self.stdout.write(self.style.SUCCESS('Successfully added all training modules')) 