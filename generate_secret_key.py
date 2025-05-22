from django.core.management.utils import get_random_secret_key

# Generate a new secret key
secret_key = get_random_secret_key()
print("\nYour new Django secret key is:")
print(secret_key)
print("\nCopy this key and use it as your DJANGO_SECRET_KEY in .env file") 