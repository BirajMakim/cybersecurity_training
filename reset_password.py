import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cybersecurity_training.settings')
django.setup()

from django.contrib.auth.models import User

def reset_password(username, new_password):
    try:
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        print(f"\nPassword has been reset for user: {username}")
        print("You can now log in with your new password")
    except User.DoesNotExist:
        print(f"\nUser '{username}' not found in the database")

if __name__ == "__main__":
    username = input("Enter username: ")
    new_password = input("Enter new password: ")
    reset_password(username, new_password) 