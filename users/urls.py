# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('accounts/login/', views.user_login, name='user_login'),
    path('signup/', views.user_registration, name='user_registration'),
    path('logout/', views.user_logout, name='user_logout'),
    path('password-reset/', views.password_reset, name='password_reset'),
    
    path('activate/<str:token>/', views.activate, name='activate'),
    
    path('profile/<str:username>', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    path('staff/approvals/', views.staff_approval_list, name='staff_approval_list'),
    path('staff/approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('staff/reject/<int:user_id>/', views.reject_user, name='reject_user'),
]

