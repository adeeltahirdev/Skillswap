from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('skills/', views.skill_list, name='skill_list'),
    path('skills/my-skills/', views.my_skills, name='my_skills'),
    path('skills/suggested-matches/', views.suggested_matches, name='suggested_matches'),
    path('<int:pk>/', views.skill_detail, name='skill_detail'),
]
