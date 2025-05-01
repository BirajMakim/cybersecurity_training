from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse

# This middleware is no longer needed as we want to enforce email verification
# class BypassActivationMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
# 
#     def __call__(self, request):
#         # Skip activation check for login and register views
#         if request.path in [reverse('accounts:login'), reverse('accounts:register')]:
#             return self.get_response(request)
#             
#         response = self.get_response(request)
#         return response 