from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.mail import send_mail
from .models import BlogPost, Course, Lesson, Project, Quiz, Question, Answer, BotMessage, UserProgress, UserProfile, PROPayment
from .forms import CourseForm, UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import json
import uuid
import random


def pro_upgrade(request):
    """PRO upgrade sahifasi"""
    return render(request, 'pro_upgrade.html')


@login_required
def pro_payment(request):
    """PRO to'lov qilish va tasdiqlash"""
    if request.method == 'POST':
        amount = request.POST.get('amount', '99000')
        payment_method = request.POST.get('payment_method', 'card')
        
        transaction_id = f"PRO-{uuid.uuid4().hex[:12].upper()}"
        
        payment = PROPayment.objects.create(
            user=request.user,
            amount=amount,
            payment_method=payment_method,
            transaction_id=transaction_id,
            is_verified=True
        )
        
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        from datetime import timedelta
        profile.pro_expires = timezone.now() + timedelta(days=30)
        profile.save()
        
        return render(request, 'pro_success.html', {
            'transaction_id': transaction_id,
            'amount': amount
        })
    
    return redirect('pro_upgrade')


@login_required
def make_user_vip(request, user_id):
    """Foydalanuvchini VIP qilish (admin uchun)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Ruxsat yoq'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    profile.is_vip = True
    profile.vip_since = timezone.now()
    profile.pro_expires = None  # VIP uchun expiry yo'q
    profile.save()
    
    # Foydalanuvchini logout qilish (sessionni tozalash uchun)
    from django.contrib.sessions.models import Session
    
    # User ID bo'yicha sessionlarni topish va o'chirish
    all_sessions = Session.objects.all()
    for session in all_sessions:
        session_data = session.get_decoded()
        if session_data.get('_auth_user_id') == str(user.id):
            session.delete()
    
    return JsonResponse({'success': True, 'message': f'{user.username} VIP qilindi!', 'logged_out': True})


@login_required
def make_user_pro(request, user_id):
    """Foydalanuvchini PRO qilish (30 kun muddat)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Ruxsat yoq'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    # PRO qilish - VIP emas, lekin 30 kun muddat
    profile.is_vip = False
    profile.vip_since = None
    from datetime import timedelta
    profile.pro_expires = timezone.now() + timedelta(days=30)
    profile.save()
    
    # Foydalanuvchini logout qilish (sessionni tozalash uchun)
    from django.contrib.sessions.models import Session
    
    # User ID bo'yicha sessionlarni topish va o'chirish
    all_sessions = Session.objects.all()
    for session in all_sessions:
        session_data = session.get_decoded()
        if session_data.get('_auth_user_id') == str(user.id):
            session.delete()
    
    return JsonResponse({'success': True, 'message': f'{user.username} PRO qilindi! (30 kun)', 'logged_out': True})


@login_required
def send_vip_emails(request):
    """VIP foydalanuvchilarga email jo'natish (admin uchun)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Ruxsat yoq'}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            subject = data.get('subject', 'MerenHub dan xabar')
            message = data.get('message', '')
            
            vip_profiles = UserProfile.objects.filter(is_vip=True)
            emails = []
            
            for profile in vip_profiles:
                if profile.vip_emails:
                    custom_emails = [e.strip() for e in profile.vip_emails.split(',') if e.strip()]
                    emails.extend(custom_emails)
                emails.append(profile.user.email)
            
            emails = list(set(emails))
            
            if emails:
                send_mail(
                    subject,
                    message,
                    'merenhub2025@gmail.com',
                    emails,
                    fail_silently=False,
                )
                return JsonResponse({'success': True, 'sent_count': len(emails)})
            else:
                return JsonResponse({'success': False, 'error': 'Email topilmadi'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


def admin_users(request):
    """Admin foydalanuvchilar boshqaruv sahifasi"""
    if not request.user.is_staff:
        return render(request, 'index.html')
    return render(request, 'admin_users.html')


def users_list_api(request):
    """Barcha foydalanuvchilar ro'yxati (API)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Ruxsat yoq'}, status=403)
    
    users = User.objects.all().select_related('profile').order_by('-date_joined')
    
    users_data = []
    for user in users:
        try:
            profile = user.profile
            is_vip = profile.is_vip
            is_banned = profile.is_banned
            pro_expires = profile.pro_expires
            # PRO tekshirish (is_vip yoki pro_expires)
            is_pro = profile.is_pro() if hasattr(profile, 'is_pro') else (profile.is_vip or (profile.pro_expires and profile.pro_expires > timezone.now()))
        except UserProfile.DoesNotExist:
            is_vip = False
            is_banned = False
            pro_expires = None
            is_pro = False
        
        users_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_vip': is_vip,
            'is_pro': is_pro,
            'pro_expires': pro_expires.strftime('%Y-%m-%d') if pro_expires else None,
            'is_banned': is_banned,
            'date_joined': user.date_joined.strftime('%Y-%m-%d')
        })
    
    return JsonResponse({'success': True, 'users': users_data})


@login_required
def remove_user_vip(request, user_id):
    """Foydalanuvchidan VIP olib tashlash"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Ruxsat yoq'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    profile.is_vip = False
    profile.save()
    
    return JsonResponse({'success': True, 'message': f'{user.username} dan VIP olib tashlandi!'})


@login_required
def ban_user(request, user_id):
    """Foydalanuvchini ban qilish"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Ruxsat yoq'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    
    try:
        data = json.loads(request.body)
        reason = data.get('reason', 'Sabab ko\'rsatilmagan')
    except:
        reason = 'Sabab ko\'rsatilmagan'
    
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    profile.is_banned = True
    profile.ban_reason = reason
    profile.banned_at = timezone.now()
    profile.save()
    
    return JsonResponse({'success': True, 'message': f'{user.username} ban qilindi!'})


@login_required
def unban_user(request, user_id):
    """Foydalanuvchini ban dan chiqarish"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Ruxsat yoq'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    profile.is_banned = False
    profile.ban_reason = ''
    profile.save()
    
    return JsonResponse({'success': True, 'message': f'{user.username} ban dan chiqarildi!'})
