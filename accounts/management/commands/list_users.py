from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Lists all users in the database'

    def handle(self, *args, **options):
        users = User.objects.all()
        if users:
            self.stdout.write(self.style.SUCCESS('Users in database:'))
            for user in users:
                self.stdout.write(f'Username: {user.username}, Email: {user.email}, Active: {user.is_active}')
        else:
            self.stdout.write(self.style.WARNING('No users found in database')) 