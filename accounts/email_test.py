from django.core.mail import send_mail
from django.conf import settings

def test_email():
    try:
        send_mail(
            'Test Email',
            'This is a test email from your Django application.',
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER],  # Sending to yourself
            fail_silently=False,
        )
        print("Test email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {str(e)}")

if __name__ == "__main__":
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cybersecurity_training.settings')
    django.setup()
    test_email() 