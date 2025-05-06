from django.db import migrations
from django.utils.text import slugify

def create_initial_training_modules(apps, schema_editor):
    TrainingModule = apps.get_model('modules', 'TrainingModule')
    modules = [
        {
            'title': 'Password Security',
            'description': 'Learn how to create strong, unique passwords and securely manage them.',
            'duration': 15,
            'difficulty': 'beginner',
            'icon': 'bi-key',
        },
        {
            'title': 'Phishing Awareness',
            'description': 'Spot and avoid phishing emails, fake links, and dangerous attachments.',
            'duration': 20,
            'difficulty': 'beginner',
            'icon': 'bi-envelope-exclamation',
        },
        {
            'title': 'Multi-Factor Authentication (MFA)',
            'description': 'Understand the benefits of MFA and how to set it up across services.',
            'duration': 10,
            'difficulty': 'beginner',
            'icon': 'bi-shield-lock',
        },
        {
            'title': 'Social Engineering',
            'description': 'Discover how attackers manipulate users and how to resist social engineering.',
            'duration': 20,
            'difficulty': 'intermediate',
            'icon': 'bi-person-bounding-box',
        },
        {
            'title': 'Insider Threats',
            'description': 'Identify accidental or malicious insider risks and how to report them.',
            'duration': 15,
            'difficulty': 'intermediate',
            'icon': 'bi-people',
        },
        {
            'title': 'Data Protection and Privacy',
            'description': 'Learn to handle personal and sensitive information securely.',
            'duration': 25,
            'difficulty': 'intermediate',
            'icon': 'bi-shield-check',
        },
        {
            'title': 'Malware and Ransomware',
            'description': 'Get familiar with common types of malware and how to prevent infections.',
            'duration': 20,
            'difficulty': 'advanced',
            'icon': 'bi-bug',
        },
    ]
    for m in modules:
        TrainingModule.objects.get_or_create(
            title=m['title'],
            defaults={
                'description': m['description'],
                'duration': m['duration'],
                'difficulty': m['difficulty'],
                'icon': m['icon'],
                'slug': slugify(m['title']),
            }
        )

class Migration(migrations.Migration):
    dependencies = [
        ('modules', '0002_alter_trainingmodule_options_and_more'),
    ]
    operations = [
        migrations.RunPython(create_initial_training_modules),
    ] 