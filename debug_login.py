import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cybersecurity_training.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

def debug_login(username, password):
    print("\n=== Login Debug Information ===")
    
    # 1. Check if user exists
    try:
        user = User.objects.get(username=username)
        print(f"1. User found in database: {username}")
        print(f"   - Email: {user.email}")
        print(f"   - Is Active: {user.is_active}")
        print(f"   - Last Login: {user.last_login}")
    except User.DoesNotExist:
        print(f"1. User '{username}' not found in database")
        return

    # 2. Try to authenticate
    auth_user = authenticate(username=username, password=password)
    if auth_user:
        print("2. Authentication successful")
        print(f"   - User authenticated: {auth_user.username}")
    else:
        print("2. Authentication failed")
        print("   - Possible reasons:")
        print("     * Password is incorrect")
        print("     * User is not active")
        print("     * Authentication backend issue")

    # 3. Check password hash
    print(f"\n3. Password hash in database: {user.password}")

    # 4. Try to verify password directly
    if user.check_password(password):
        print("4. Password verification successful")
    else:
        print("4. Password verification failed")

if __name__ == "__main__":
    username = input("Enter username to debug: ")
    password = input("Enter password: ")
    debug_login(username, password) 