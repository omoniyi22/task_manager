from django.urls import path
from . import views

admin_urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('plans/', views.plan_list, name='plan_list'),
    path('plans/create/', views.plan_create, name='plan_create'),
    path('plans/<int:plan_id>/', views.plan_detail, name='plan_detail'),
    path('plans/<int:plan_id>/delete/', views.delete_plan, name='delete_plan'),
]