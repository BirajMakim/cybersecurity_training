from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import ChatMessage
import requests
import json
from django.conf import settings
import os

# Create your views here.

@login_required
def chat_view(request):
    messages = ChatMessage.objects.filter(user=request.user)[:10]
    return render(request, 'chatbot/chat.html', {'messages': messages})

@login_required
@require_POST
def send_message(request):
    print("OPENROUTER_API_KEY from env:", os.getenv('OPENROUTER_API_KEY'))
    print("OPENROUTER_API_KEY from settings:", getattr(settings, 'OPENROUTER_API_KEY', None))
    message = request.POST.get('message', '')
    if not message:
        print("No message provided in POST data.")
        return JsonResponse({'error': 'Message is required'}, status=400)

    # OpenRouter API configuration
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://127.0.0.1:8000",  # or your deployed site URL
        "X-Title": "Cybersecurity Training Platform",
        "Content-Type": "application/json"
    }
    print("API URL:", api_url)
    print("Headers:", headers)
    
    data = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [
            {"role": "user", "content": message}
        ]
    }
    print("Payload:", data)

    try:
        response = requests.post(api_url, headers=headers, json=data)
        print("API response status code:", response.status_code)
        print("API response text:", response.text)
        response.raise_for_status()
        ai_response = response.json()['choices'][0]['message']['content']

        # Save the message and response
        chat_message = ChatMessage.objects.create(
            user=request.user,
            message=message,
            response=ai_response
        )

        return JsonResponse({
            'message': message,
            'response': ai_response,
            'timestamp': chat_message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    except Exception as e:
        print("Error in send_message:", e)
        return JsonResponse({'error': str(e)}, status=500)
