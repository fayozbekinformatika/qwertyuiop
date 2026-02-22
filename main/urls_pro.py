from django.urls import path
from main import views_pro

urlpatterns = [
    path('pro/', views_pro.pro_upgrade, name='pro_upgrade'),
    path('pro/payment/', views_pro.pro_payment, name='pro_payment'),
    path('admin/users/', views_pro.admin_users, name='admin_users'),
    path('api/users/', views_pro.users_list_api, name='users_list_api'),
    path('api/make-vip/<int:user_id>/', views_pro.make_user_vip, name='make_user_vip'),
    path('api/make-pro/<int:user_id>/', views_pro.make_user_pro, name='make_user_pro'),
    path('api/remove-vip/<int:user_id>/', views_pro.remove_user_vip, name='remove_user_vip'),
    path('api/ban-user/<int:user_id>/', views_pro.ban_user, name='ban_user'),
    path('api/unban-user/<int:user_id>/', views_pro.unban_user, name='unban_user'),
    path('api/send-vip-emails/', views_pro.send_vip_emails, name='send_vip_emails'),
]
