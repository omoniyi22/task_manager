from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication
    path('signup/', views.staff_signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Dashboard - root URL
    path('', views.dashboard, name='dashboard'),
    
    # Admin URLs (using 'manage' instead of 'admin' to avoid conflict with Django admin)
    path('manage/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage/plans/', views.plan_list, name='plan_list'),
    path('manage/plans/create/', views.plan_create, name='plan_create'),
    path('manage/plans/<int:plan_id>/', views.plan_detail, name='plan_detail'),
    path('manage/plans/<int:plan_id>/delete/', views.delete_plan, name='delete_plan'),
    
    # Staff URLs
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/plans/<int:plan_id>/', views.staff_plan_detail, name='staff_plan_detail'),
    path('staff/tasks/<int:task_id>/update/', views.update_task, name='update_task'),
]