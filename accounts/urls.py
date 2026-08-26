from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.user_profile, name='profile'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('logout/', views.logout_view, name='logout'),
    
    
      # Temporary placeholder URLs
    path('edit-profile/', lambda request: redirect('profile'), name='edit_profile'),
    path('my-skills/', lambda request: redirect('profile'), name='my_skills'),
    path('add-skill/', lambda request: redirect('profile'), name='add_skill'),
    path('skill-detail/<int:pk>/', lambda request, pk: redirect('profile'), name='skill_detail'),
]