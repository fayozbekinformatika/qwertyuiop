from main import views
from main import views_pro
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Custom admin URLs (must be BEFORE admin.site.urls)
    path('admin/users/', views_pro.admin_users, name='admin_users'),
    
    # Django admin
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('index.html', views.index),
    path('blog.html', views.blog, name='blog'),
    path('learning/', views.learning, name='learning'),
    path('learning/<slug:course_slug>/<slug:lesson_slug>/', views.lesson_detail, name='lesson_detail'),
    path('quiz/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('test_bot.html', views.test_bot, name='test_bot'),
    path('test-bot/', views.test_bot, name='test_bot'),
    path('add_course/', views.add_course, name='add_course'),
    path('run-simulation/', views.run_bot_simulation, name='run_bot_simulation'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html', next_page='index'), name='login'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html', next_page='index'), name='login'),
    path('accounts/logout/', views.custom_logout, name='logout'),
    path('accounts/profile/', views.profile, name='profile'),
    path('toggle-theme/', views.toggle_theme, name='toggle_theme'),
    path('register/', views.register, name='register'),
    
    # Password reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    
    # Change password URLs
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='password_change.html', success_url='done'), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),
    
    # Bot message API
    path('api/save-bot-message/', views.save_bot_message, name='save_bot_message'),
    path('bot-messages/', views.bot_messages_list, name='bot_messages'),
    
    # Lesson progress
    path('complete-lesson/<int:lesson_id>/', views.complete_lesson, name='complete_lesson'),
    
    # PRO URLs (using views_pro)
    path('pro/', views_pro.pro_upgrade, name='pro_upgrade'),
    path('pro/payment/', views_pro.pro_payment, name='pro_payment'),
    path('api/users/', views_pro.users_list_api, name='users_list'),
    path('api/make-vip/<int:user_id>/', views_pro.make_user_vip, name='make_user_vip'),
    path('api/make-pro/<int:user_id>/', views_pro.make_user_pro, name='make_user_pro'),
    path('api/remove-vip/<int:user_id>/', views_pro.remove_user_vip, name='remove_vip'),
    path('api/ban-user/<int:user_id>/', views_pro.ban_user, name='ban_user'),
    path('api/unban-user/<int:user_id>/', views_pro.unban_user, name='unban_user'),
    path('api/send-vip-emails/', views_pro.send_vip_emails, name='send_vip_emails'),
]
