from django.shortcuts import render
from .models import UserProfile

def theme_context(request):
    theme = request.session.get('theme', 'dark')
    return {'theme': theme}


def user_pro_context(request):
    """Barcha sahifalarga PRO/VIP ma'lumotlarini qo'shadi"""
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            return {
                'is_pro': profile.is_pro(),
                'is_vip': profile.is_vip,
                'pro_expires': profile.pro_expires,
            }
        except UserProfile.DoesNotExist:
            pass
    return {'is_pro': False, 'is_vip': False, 'pro_expires': None}
