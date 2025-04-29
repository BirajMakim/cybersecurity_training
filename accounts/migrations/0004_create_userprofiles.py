from django.db import migrations

def create_userprofiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('accounts', 'UserProfile')
    
    for user in User.objects.all():
        UserProfile.objects.get_or_create(user=user)

def reverse_userprofiles(apps, schema_editor):
    UserProfile = apps.get_model('accounts', 'UserProfile')
    UserProfile.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0003_alter_profile_user_useractivitylog_userbadge_and_more'),
    ]

    operations = [
        migrations.RunPython(create_userprofiles, reverse_userprofiles),
    ] 