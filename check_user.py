import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cybersecurity_training.settings')
django.setup()

from django.contrib.auth.models import User

def check_user(username):
    try:
        user = User.objects.get(username=username)
        print(f"\nUser found: {username}")
        print(f"Email: {user.email}")
        print(f"First Name: {user.first_name}")
        print(f"Last Name: {user.last_name}")
        print(f"Is Active: {user.is_active}")
        print(f"Last Login: {user.last_login}")
        print(f"Date Joined: {user.date_joined}")
        print(f"Password Hash: {user.password}")
    except User.DoesNotExist:
        print(f"\nUser '{username}' not found in the database")

if __name__ == "__main__":
    username = input("Enter username to check: ")
    check_user(username) 