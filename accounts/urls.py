from django.urls import path
from accounts import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile URLs
    path('profile/', views.user_profile, name='profile'),
    path('profile/<str:username>/', views.user_profile, name='profile_detail'),
    
    # AJAX Endpoints for profile management
    path('api/update-profile/', views.update_profile, name='update_profile'),
    path('api/update-avatar/', views.update_avatar, name='update_avatar'),
    path('api/add-skill/', views.add_skill, name='add_skill'),
    path('api/delete-skill/<int:skill_id>/', views.delete_skill, name='delete_skill'),
]

