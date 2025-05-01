from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active)
        )

account_activation_token = AccountActivationTokenGenerator()

def redirect_to_login(request):
    messages.error(request, 'Your account is not active. Please check your email for activation link.')
    return redirect(reverse('accounts:login')) 