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


def get_user_profile(request):
    """Foydalanuvchi PRO/VIP holatini qaytaradi"""
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            return {
                'is_pro': profile.is_pro(),
                'is_vip': profile.is_vip,
                'is_banned': profile.is_banned,
                'pro_expires': profile.pro_expires,
            }
        except UserProfile.DoesNotExist:
            pass
    return {'is_pro': False, 'is_vip': False, 'is_banned': False, 'pro_expires': None}


def index(request):
    # Ban check
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            if profile.is_banned:
                auth_logout(request)
                return render(request, 'banned.html', {'reason': profile.ban_reason})
        except UserProfile.DoesNotExist:
            pass
    
    project_count = Project.objects.count()
    projects = Project.objects.all().order_by('-created_at')
    profile_data = get_user_profile(request)
    return render(request, 'index.html', {
        'project_count': project_count, 
        'projects': projects,
        **profile_data
    })

def blog(request):
    posts = BlogPost.objects.all()
    profile_data = get_user_profile(request)
    return render(request, 'blog.html', {
        'posts': posts,
        **profile_data
    })

@login_required
def learning(request):
    courses = Course.objects.all()
    for course in courses:
        course.user_progress = course.get_progress_for_user(request.user)
    profile_data = get_user_profile(request)
    return render(request, 'learning.html', {
        'courses': courses,
        **profile_data
    })

@login_required
def lesson_detail(request, course_slug, lesson_slug):
    course = Course.objects.get(slug=course_slug)
    lesson = Lesson.objects.get(course=course, slug=lesson_slug)
    lessons = Lesson.objects.filter(course=course).order_by('order')
    
    lesson_list = list(lessons)
    current_index = lesson_list.index(lesson)
    previous_lesson = lesson_list[current_index - 1] if current_index > 0 else None
    next_lesson = lesson_list[current_index + 1] if current_index < len(lesson_list) - 1 else None
    
    is_completed = UserProgress.objects.filter(
        user=request.user, 
        lesson=lesson, 
        completed=True
    ).exists()
    
    profile_data = get_user_profile(request)
    return render(request, 'lesson_detail.html', {
        'course': course, 
        'lesson': lesson, 
        'lessons': lessons,
        'previous_lesson': previous_lesson,
        'next_lesson': next_lesson,
        'is_completed': is_completed,
        **profile_data
    })


@login_required
def complete_lesson(request, lesson_id):
    if request.method == 'POST':
        lesson = get_object_or_404(Lesson, id=lesson_id)
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'completed': True}
        )
        if not created and not progress.completed:
            progress.completed = True
            progress.save()
        return JsonResponse({'success': True, 'progress': lesson.course.get_progress_for_user(request.user)})
    return JsonResponse({'success': False}, status=400)


@login_required
def quiz_list(request):
    quizzes = Quiz.objects.all().select_related('course')
    profile_data = get_user_profile(request)
    return render(request, 'quiz_list.html', {
        'quizzes': quizzes,
        **profile_data
    })

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()
    
    if request.method == 'POST':
        score = 0
        total = 0
        for question in questions:
            total += 1
            selected_answer_id = request.POST.get(f'question_{question.id}')
            if selected_answer_id:
                answer = get_object_or_404(Answer, id=selected_answer_id)
                if answer.is_correct:
                    score += 1
        
        percentage = int((score / total) * 100) if total > 0 else 0
        return render(request, 'quiz_result.html', {
            'quiz': quiz,
            'score': score,
            'total': total,
            'percentage': percentage
        })
    
    profile_data = get_user_profile(request)
    return render(request, 'take_quiz.html', {
        'quiz': quiz, 
        'questions': questions,
        **profile_data
    })

@login_required
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning')
    else:
        form = CourseForm()
    profile_data = get_user_profile(request)
    return render(request, 'add_course.html', {
        'form': form,
        **profile_data
    })

def test_bot(request):
    profile_data = get_user_profile(request)
    return render(request, 'test_bot.html', context=profile_data)

def run_bot_simulation(request):
    simulation_result = "Bot simulyatsiyasi muvaffaqiyatli yakunlandi!"
    profile_data = get_user_profile(request)
    return render(request, 'test_bot.html', {
        'simulation_result': simulation_result,
        **profile_data
    })

def custom_logout(request):
    auth_logout(request)
    return redirect('index')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def profile(request):
    profile_data = get_user_profile(request)
    return render(request, 'profile.html', **profile_data)

def toggle_theme(request):
    if request.method == 'POST':
        theme = request.POST.get('theme', 'dark')
        request.session['theme'] = theme
    return redirect(request.META.get('HTTP_REFERER', 'index'))


@csrf_exempt
def save_bot_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user if request.user.is_authenticated else None
            bot_message = BotMessage.objects.create(
                user=user,
                session_id=data.get('session_id', ''),
                user_message=data.get('user_message', ''),
                bot_code=data.get('bot_code', ''),
                bot_reply=data.get('bot_reply', '')
            )
            return JsonResponse({'success': True, 'id': bot_message.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


@login_required
def bot_messages_list(request):
    # Admin (staff) barcha xabarlarni ko'radi, oddiy foydalanuvchi faqat ozi yozganlarini
    if request.user.is_staff:
        messages = BotMessage.objects.all().order_by('-created_at')
    else:
        messages = BotMessage.objects.filter(user=request.user).order_by('-created_at')
    
    profile_data = get_user_profile(request)
    return render(request, 'bot_messages.html', {
        'messages': messages,
        **profile_data
    })


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
    profile.save()
    
    return JsonResponse({'success': True, 'message': f'{user.username} VIP qilindi!'})


@login_required
def remove_vip(request, user_id):
    """Foydalanuvchidan VIP olib tashlash (admin uchun)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Ruxsat yoq'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    
    try:
        profile = user.profile
        profile.is_vip = False
        profile.vip_since = None
        profile.save()
        return JsonResponse({'success': True, 'message': f'{user.username} dan VIP olib tashlandi!'})
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Profile topilmadi'}, status=404)


@login_required
def ban_user(request, user_id):
    """Foydalanuvchini ban qilish (admin uchun)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Ruxsat yoq'}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            reason = data.get('reason', 'Ban qilindi')
            
            user = get_object_or_404(User, id=user_id)
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            profile.is_banned = True
            profile.ban_reason = reason
            profile.banned_at = timezone.now()
            profile.banned_by = request.user
            profile.save()
            
            return JsonResponse({'success': True, 'message': f'{user.username} ban qilindi!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


@login_required
def unban_user(request, user_id):
    """Foydalanuvchini ban dan chiqarish (admin uchun)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Ruxsat yoq'}, status=403)
    
    user = get_object_or_404(User, id=user_id)
    
    try:
        profile = user.profile
        profile.is_banned = False
        profile.ban_reason = ''
        profile.banned_at = None
        profile.banned_by = None
        profile.save()
        return JsonResponse({'success': True, 'message': f'{user.username} ban dan chiqarildi!'})
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Profile topilmadi'}, status=404)


@login_required
def user_list(request):
    """Barcha foydalanuvchilar ro'yxati (admin uchun)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Ruxsat yoq'}, status=403)
    
    users = User.objects.all().select_related('profile')
    user_data = []
    
    for user in users:
        try:
            profile = user.profile
            user_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_vip': profile.is_vip,
                'is_banned': profile.is_banned,
                'ban_reason': profile.ban_reason,
                'date_joined': user.date_joined.strftime('%Y-%m-%d'),
            })
        except UserProfile.DoesNotExist:
            user_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_vip': False,
                'is_banned': False,
                'ban_reason': '',
                'date_joined': user.date_joined.strftime('%Y-%m-%d'),
            })
    
    return JsonResponse({'success': True, 'users': user_data})


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
