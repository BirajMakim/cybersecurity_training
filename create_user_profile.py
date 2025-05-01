import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cybersecurity_training.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

def create_user_profile(username):
    try:
        user = User.objects.get(username=username)
        # Check if user_profile already exists
        if hasattr(user, 'user_profile'):
            print(f"\nUser '{username}' already has a profile")
            return
            
        # Create new user profile
        profile = UserProfile.objects.create(user=user)
        profile.calculate_profile_complete()
        print(f"\nCreated UserProfile for user: {username}")
        print(f"Profile completion: {profile.profile_complete}%")
    except User.DoesNotExist:
        print(f"\nUser '{username}' not found in the database")

if __name__ == "__main__":
    username = input("Enter username to create profile for: ")
    create_user_profile(username) 