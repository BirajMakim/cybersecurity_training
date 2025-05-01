import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cybersecurity_training.settings')
django.setup()

from django.contrib.auth.models import User

def activate_user(username):
    try:
        user = User.objects.get(username=username)
        user.is_active = True
        user.save()
        print(f"\nUser '{username}' has been activated successfully!")
        print("You can now log in with your username and password")
    except User.DoesNotExist:
        print(f"\nUser '{username}' not found in the database")

if __name__ == "__main__":
    username = input("Enter username to activate: ")
    activate_user(username) 